from ssl import _OPENSSL_API_VERSION
from asciimatics.screen import Screen
import fetchSources as Sources
import fetchLive as Fetch
from math import ceil
import threading
import datetime
import time
import json
import copy

class Graph:
    def __init__(self, x: int, y: int, pair: dict, screen: Screen):
        self.x: int = x
        self.y: int = y
        with open('config.jsonc') as config:
            data = json.load(config)
            self.width: int = data['market']['width']
            self.height: int = data['market']['height']
            self.slice: int = data['market']['slice']
            self.rounded: bool = data['boxes']['rounded']
        
        self.pair: dict = pair
        self.source: str = self.pair['source']
        
        self.screen: Screen = screen
        self.rendering: bool = False
        
        self.history: dict[int, list] = {}
        self.start: datetime.datetime = datetime.datetime.now() # DONE fix: lock on server time
        self.now: datetime.datetime = datetime.datetime.now()
        
        self.selected: bool = False
        self.hovered: int = 0
        self.max_listed = 15
        
        pairs = {i: [] for i in Sources.SOURCES}
        self.choice: dict = {
            'hovered': 0,
            'number': 0,
            'scroll': 0,
            'pairs': pairs,
            'filters': {
                'base': "",
                'quote': "",
                'name': ""
            },
            'filter': ""
        }
        
        pass

    def fetch_data(self):

        # return # test to see if lags exists

        if self.pair['source'] in Sources.SOURCES.keys():
            try:

                def _fetch():
                    data = Fetch.fetch(self.pair['source'], self.pair['name'])

                    while self.rendering:
                        time.sleep(0.05)

                    self.add_data(data)

                thread = threading.Thread(target=_fetch, args=())
                thread.start()

                # data = Fetch.fetch(self.pair['source'], self.pair['name']) # DONE edit, create lags due to response delay (thread?)

                # self.add_data(data)

            except json.JSONDecodeError: # not foratted response
                pass
            except: # connection error (probably)
                pass

        return
    
    def add_data(self, data: dict):

        if self.history == {}: # first data on this value
            self.start = data['time']
        
        slice_id: int = int((data['time'] - self.start).total_seconds() // self.slice)
        try:
            self.history[slice_id].append(data)
        except KeyError:
            self.history[slice_id] = [data]
        
        return
    
    def render_frame(self):

        self.rendering = True
        
        self.screen.clear_buffer(Screen.COLOUR_WHITE, 0, Screen.COLOUR_BLACK)
        
        self.render_box()
        self.render_graph()
        self.render_data()
        if self.selected: self.render_choices()

        # self.screen.print_at(self.history, 0, 0)
        # self.screen.print_at(' .' * 45, 0, 0)
        
        # self.screen.print_at(self.choice['number'], 0, 10)
        # self.screen.print_at(self.hovered, 0, 11)
        # self.screen.print_at(self.selected, 0, 12)
        # self.screen.print_at(f"{self.choice['hovered']} {self.choice['number']} {self.choice['scroll']}", 0, 13)
        # self.screen.print_at(f"{self.choice['filters']['base']} {self.choice['filters']['quote']}", 0, 14)
        
        self.screen.refresh()

        self.rendering = False
        
        return
    
    def render_data(self):
        
        base = self.pair['base']
        quote = self.pair['quote']
        name = self.pair['name']
        type = self.pair['type']
        
        if len(name) > 10:
            name = name[:8] + '..'
        if len(quote) > 10:
            quote = quote[:8] + '..'
        if len(base) > 10:
            base = quote[:8] + '..'
        
        colors = [
            (Screen.COLOUR_WHITE, Screen.COLOUR_BLACK),
            (Screen.COLOUR_WHITE, Screen.COLOUR_BLACK),
            (Screen.COLOUR_WHITE, Screen.COLOUR_BLACK)
        ]
        
        if self.hovered != 0:
            colors[self.hovered - 1] = (Screen.COLOUR_BLACK, Screen.COLOUR_WHITE)
        
        self.screen.print_at(base, self.x + self.width - len(base), self.y + 1, colors[0][0], bg=colors[0][1])
        self.screen.print_at(quote, self.x + self.width - len(quote), self.y + 2, colors[1][0], bg=colors[1][1])
        self.screen.print_at(name, self.x + self.width - len(name), self.y + 3, colors[2][0], bg=colors[2][1])
        self.screen.print_at(self.source.capitalize(), self.x + self.width - len(self.source), self.y + 4)
        self.screen.print_at(type, self.x + self.width - len(type), self.y + 5)
        
        return
    
    def render_graph(self):
        
        OHLC = {} # DONE add last value of last candle to next fro continuity
        temp = copy.deepcopy(self.history) # prevent error for size change (thread)
        _start = max(0, len(temp) - self.width + 12)
        _stop = len(temp)
        datas = list(temp.values())
        for _slice in range(_start, _stop):
        # for _slice, data in temp.items():
            try:
                data = datas[_slice]
            except:
                continue

            try:
                last_data = OHLC[_slice - 1]
                data.append({
                    'value': last_data['close'],
                    'time': sorted(self.history[_slice - 1], key=lambda a: (a['time']-datetime.datetime(1970,1,1)).total_seconds())[-1]['time'] # time of last transaction
                })
            except KeyError: # last slice doen't exist
                pass

            _value = sorted(data, key=lambda a: a['value']) # DONE convert to float (comes in as str...) / directly in fetchSources?
            _time = sorted(data, key=lambda a: (a['time']-datetime.datetime(1970,1,1)).total_seconds())


            _max = _value[-1]['value']
            _min = _value[0]['value'] # DONE fix low (doesn't render)
            _open = _time[0]['value']
            _close = _time[-1]['value']

            OHLC[_slice] = {
                'open': _open,
                'high': _max,
                'low': _min,
                'close': _close
            }

        if len(OHLC) == 0: return

        start = list(OHLC.values())[0]['open']
        graph_max = max(map(lambda a: a['high'], OHLC.values()))
        graph_min = min(map(lambda a: a['low'], OHLC.values()))

        step = (self.height - 3) / (graph_max - graph_min + 1)

        for i in range(1, self.width - 11):
            self.screen.print_at('┄', i, ceil((graph_max - start) * step) + 1, 2 if list(OHLC.values())[-1]['close'] > start else 1)

        for _slice in range(_start, _stop):
            data = OHLC[_slice]

            low_step = round((graph_max - data['low']) * step)
            high_step = round((graph_max - data['high']) * step)
            open_step = round((graph_max - data['open']) * step)
            close_step = round((graph_max - data['close']) * step)

            rise = data['open'] < data['close']
            _min = min(open_step, close_step)
            _max = max(open_step, close_step)

            _x = _slice + self.x + 1 + min(0, self.width - 12 - _stop)

            for i in range(high_step, _min):
                self.screen.print_at("│", _x, i + self.y + 1, 2 if rise else 1)

            for i in range(_min, _max):
                self.screen.print_at("█", _x, i + self.y + 1, 2 if rise else 1)
            
            for i in range(_max, low_step):
                self.screen.print_at("│", _x, i + self.y + 1, 2 if rise else 1)

            # usable: self.height - 2

        # # # # OHLC data render
        
        data = list(OHLC.values())[-1]
        placeholders = {
            'O': 'open',
            'H': 'high',
            'L': 'low',
            'C': 'close'
        }

        _x = self.x + 1
        _y = self.y + self.height - 1
        for _key, _value in placeholders.items():
            self.screen.print_at(_key, _x, _y, 2 if rise else 1)
            self.screen.print_at(f': {data[_value]}', _x + 1, _y)
            _x += len(str(data[_value])) + 4

        _x += 3
        self.screen.print_at('Start', _x, _y, 2 if list(OHLC.values())[-1]['close'] > start else 1)
        self.screen.print_at(f': {start}', _x + 5, _y)

        # # # # Global stats

        percentage = round(1 - data['close'] / start, 2)
        if percentage > 0:
            percentage = "+" + str(percentage) + "%"
        else:
            percentage = str(percentage) + "%"

        change = round(data['close'] - start, 2)
        if change > 0:
            change = "+" + str(change)
        else:
            change = str(change)
        
        self.screen.print_at(percentage, self.x + self.width - len(percentage), _y - 2, 2 if list(OHLC.values())[-1]['close'] > start else 1)
        self.screen.print_at(change, self.x + self.width - len(change), _y - 1, 2 if list(OHLC.values())[-1]['close'] > start else 1)
        self.screen.print_at(data['close'], self.x + self.width - len(str(data['close'])), _y, 2 if list(OHLC.values())[-1]['close'] > start else 1)
        
        return
    
    def render_box(self):
        
        topl = '╭' if self.rounded else '┌'
        topr = '╮' if self.rounded else '┐'
        top = topl + (self.width - 12) * '─' + '┬' + 10 * '─' + topr
        
        botl = '╰' if self.rounded else '└'
        botr = '╯' if self.rounded else '┘'
        bot = botl + (self.width - 12) * '─' + '┴' + 10 * '─' + botr
        
        self.screen.print_at(top, self.x, self.y)
        self.screen.print_at(bot, self.x, self.y + self.height)
        
        for i in range(1, self.height):
            self.screen.print_at('│', self.x, self.y + i)
            self.screen.print_at('│', self.x + self.width - 11, self.y + i)
            self.screen.print_at('│', self.x + self.width, self.y + i)
        
        return
    
    def update_pair(self):
        
        pairs = sum([self.choice['pairs'][i] for i in Sources.SOURCES], [])
        new_pair = pairs[self.choice['hovered']]
        
        self.pair = new_pair
        self.source = new_pair['source']
        self.history = {}
        
        return
    
    def update_filter(self, keycode: int):
        
        filter_type = ['base', 'quote', 'name'][self.hovered - 1]
        
        if keycode in [-300, -102]: # backspace or del
            if len(self.choice['filters'][filter_type]) > 0:
                self.choice['filters'][filter_type] = self.choice['filters'][filter_type][:-1]
                self.update_choices(True)
        else:
            self.choice['filters'][filter_type] += chr(keycode).capitalize()
        
        return
    
    def update_choices(self, reset: bool = False):
        
        base_filter: str = self.choice['filters']['base']
        quote_filter: str = self.choice['filters']['quote']
        name_filter: str = self.choice['filters']['name']
        
        fc = lambda a: quote_filter in a['quote'] and base_filter in a['base'] and name_filter in a['name']
        
        if reset:
            for i in Sources.SOURCES:
                self.choice['pairs'][i] = Sources.fetch_list_from(i)
        
        pairs_number = 0        
        for i in Sources.SOURCES:
                self.choice['pairs'][i] = list(filter(fc, self.choice['pairs'][i]))
                pairs_number += len(self.choice['pairs'][i])
        
        self.choice['number'] = pairs_number
        
        return
    
    def reset_choice(self, only_hover = False):
        
        if not only_hover:
            pairs = {i: [] for i in Sources.SOURCES}
            self.choice = {
                'hovered': 0,
                'number': 0,
                'scroll': 0,
                'pairs': pairs,
                'filters': {
                    'base': "",
                    'quote': "",
                    'name': ""
                },
                'filter': ""
            }
            
        else:
            self.choice['hovered'] = 0
            self.choice['scroll'] = 0
            
        return
    
    def render_choices(self):
        
        filter_type = ['base', 'quote', 'name'][self.hovered - 1]
        current_filter = self.choice['filters'][filter_type]
        
        pairs = sum([self.choice['pairs'][i] for i in Sources.SOURCES], [])
        max_length = max([len(a['name']) for a in (pairs + [{'name':current_filter + '_'}])])
        max_length_source = max([len(a['source']) for a in (pairs + [{'source':''}])])
        
        # Background & filter
        
        for i in range(min(self.max_listed, self.choice['number']) + 1):
            self.screen.print_at(' ' * max_length, self.x + self.width - max_length, self.y + i + self.hovered, 0, 0, 7)

        _start = 1 + (self.choice['scroll'] != 0)
        _stop = self.choice['number'] + 1 if self.max_listed > (self.choice['number'] + 1) else self.max_listed + (self.choice['scroll'] == self.choice['number'] - self.max_listed)

        for i in range(_start, _stop):
            self.screen.print_at(' ' * (max_length_source + 3), self.x + self.width, self.y + i + self.hovered, 0, 0, 247) # DONE remove for arrows and input
            
        self.screen.print_at(current_filter + '_', self.x + self.width - max_length, self.y + self.hovered, 0, 0, 7)
        
            
        # if self.hovered == 1: # base
        #     self.screen.print_at(self.choice['filters']['base'] + '_', self.x + self.width - max_length, self.y + 1, 0, 0, 7)
        # elif self.hovered == 2: # quote
            # self.screen.print_at(self.choice['filters']['quote'] + '_', self.x + self.width - max_length, self.y + 2, 0, 0, 7)
        # elif self.hovered == 3: # name
            # self.screen.print_at(self.choice['filters']['name'] + '_', self.x + self.width - max_length, self.y + 3, 0, 0, 7)
            
        # Top & botom arrow # ▽△
        
        _y = self.y + self.hovered + 1
        if self.choice['number'] < self.max_listed: # no overflow
            for i in range(len(pairs)):
                element = pairs[i]['name']
                source = pairs[i]['source']
                if i == self.choice['hovered']:
                    self.screen.print_at(' ' * max_length, self.x + self.width - max_length, _y + i)
                    self.screen.print_at(element, self.x + self.width - len(element), _y + i)
                else:
                    self.screen.print_at(element, self.x + self.width - len(element), _y + i, 0, 0, 7)
                
                self.screen.print_at(' - ' + source.capitalize(), self.x + self.width, _y + i, 0, 0, 247)
                
        else: # overflow
            for i in range(self.max_listed):
                element_id = i + self.choice['scroll']
                # if element_id >= len(pairs): continue # ?? y tf did I write this?
                element_height = _y + i
                element = pairs[element_id]['name']
                source = pairs[element_id]['source']
                if element_id == self.choice['hovered']:
                    self.screen.print_at(' ' * max_length, self.x + self.width - max_length, element_height)
                    self.screen.print_at(element, self.x + self.width - len(element), element_height)
                else:
                    self.screen.print_at(element, self.x + self.width - len(element), element_height, 0, 0, 7)

                if i >= _start - 1 and i < _stop - 1:
                    self.screen.print_at(' - ' + source.capitalize(), self.x + self.width, element_height, 0, 0, 247)
                
            if self.choice['scroll']:
                self.screen.print_at(' ' * max_length, self.x + self.width - max_length, _y, 0, 0, 7)
                self.screen.print_at("△", self.x + self.width - ceil(max_length / 2), _y, 0, 0, 7)
            if self.choice['scroll'] != self.choice['number'] - self.max_listed:
                self.screen.print_at(' ' * max_length, self.x + self.width - max_length, _y + self.max_listed - 1, 0, 0, 7)
                self.screen.print_at("▽", self.x + self.width - ceil(max_length / 2), _y + self.max_listed - 1, 0, 0, 7)
        
        return
    
    def move_choice_up(self):
        
        self.choice['hovered'] = max(min(self.choice['hovered'] - 1, self.choice['number'] - 1), 0)
        if self.choice['hovered'] < self.choice['scroll'] + 1 and self.choice['scroll'] > 0:
            self.choice['scroll'] -= 1
        
        return
    
    def move_choice_down(self):
        
        self.choice['hovered'] = max(min(self.choice['hovered'] + 1, self.choice['number'] - 1), 0)
        if self.choice['hovered'] > self.max_listed + self.choice['scroll'] - 2 and self.choice["hovered"] != self.choice['number'] - 1: # idk y but it works so don't touch
            self.choice['scroll'] += 1
        
        return
    
    def key(self, code: int) -> bool:
        if not self.selected:
            if code in (ord('q'), ord('Q')):
                return True
            elif code == -301 and not self.hovered: # tab
                self.hovered = 1
        elif code == -1: # esc
            self.selected = False
            self.reset_choice()
        elif (code >= 65 and code <= 90) or (code >= 97 and code <= 122) or (code in [ord(' '), ord('-'), -300, -102]) or (code >= 48 and code <= 57):
            self.update_filter(code)
            self.reset_choice(True)
            self.update_choices()
        else:
            pass
            # self.screen.print_at(code, 0, 0)
            # self.screen.refresh()
            # time.sleep(1)
        return False
    
    def key_up(self):
        if not self.hovered: return
        if not self.selected:
            self.hovered = (self.hovered - 2) % 3 + 1
        else:
            self.move_choice_up()
        return
    
    def key_down(self):
        if not self.hovered: return
        if not self.selected:
            self.hovered = self.hovered % 3 + 1
        else:
            self.move_choice_down()
        return
    
    def key_enter(self):
        if not self.hovered: return # if market not selected
        if not self.selected: # not filtering
            if self.hovered == 1: # base
                self.choice['filters']['base'] = self.pair['base']
                self.update_choices(True)
            elif self.hovered == 2: # quote
                self.choice['filters']['quote'] = self.pair['quote']
                self.update_choices(True)
            elif self.hovered == 3: # name
                self.choice['filters']['name'] = self.pair['name']
                self.update_choices(True)
            self.selected = True
        else: # already filtering
            self.update_pair() # TODO fix is list empty
            self.selected = False
        return

# TODO:
#   [x] take sources from module Sources
#   [x] implement fetch process
#   [x] add graph
#   [x] fix graph
#   [ ] add price render
#   [ ] add OHLC render
#   [ ] add live websocket