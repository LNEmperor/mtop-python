from asciimatics.screen import Screen
import fetchSources as Sources
import fetchLive as Fetch
import time
import json

class Graph:
    def __init__(self, x: int, y: int, width: int, heigth: int, pair: dict, screen: Screen):
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.heigth: int = heigth
        self.rounded: bool = False
        
        self.pair: dict = pair
        self.source: str = self.pair['source']
        
        self.screen: Screen = screen
        
        self.history: list[dict] = []
        
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

        if self.pair['source'] in Sources.SOURCES.keys():
            try:
                data = Fetch.fetch(self.pair['name'])
            except json.JSONDecodeError:
                data = None

            self.add_data(data)

        return
    
    def add_data(self, data: dict):
        
        self.history.append(data)
        
        return
    
    def render_frame(self):
        
        self.screen.clear_buffer(Screen.COLOUR_WHITE, 0, Screen.COLOUR_BLACK)
        
        self.render_box()
        self.render_data()
        if self.selected: self.render_choices()

        self.screen.print_at(self.pair, 0, 0)
        
        # self.screen.print_at(self.choice['number'], 0, 10)
        # self.screen.print_at(self.hovered, 0, 11)
        # self.screen.print_at(self.selected, 0, 12)
        # self.screen.print_at(f"{self.choice['hovered']} {self.choice['number']} {self.choice['scroll']}", 0, 13)
        # self.screen.print_at(f"{self.choice['filters']['base']} {self.choice['filters']['quote']}", 0, 14)
        
        self.screen.refresh()
        
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
        
        # TODO
        
        return
    
    def render_box(self):
        
        topl = '╭' if self.rounded else '┌'
        topr = '╮' if self.rounded else '┐'
        top = topl + (self.width - 12) * '─' + '┬' + 10 * '─' + topr
        
        botl = '╰' if self.rounded else '└'
        botr = '╯' if self.rounded else '┘'
        bot = botl + (self.width - 12) * '─' + '┴' + 10 * '─' + botr
        
        self.screen.print_at(top, self.x, self.y)
        self.screen.print_at(bot, self.x, self.y + self.heigth)
        
        for i in range(1, self.heigth):
            self.screen.print_at('│', self.x, self.y + i)
            self.screen.print_at('│', self.x + self.width - 11, self.y + i)
            self.screen.print_at('│', self.x + self.width, self.y + i)
        
        return
    
    def update_pair(self):
        
        pairs = sum([self.choice['pairs'][i] for i in Sources.SOURCES], [])
        new_pair = pairs[self.choice['hovered']]
        
        self.pair = new_pair
        self.source = new_pair['source']
        
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
        
        # Background & filter
        
        for i in range(min(self.max_listed, self.choice['number']) + 1):
            self.screen.print_at(' ' * max_length, self.x + self.width - max_length, self.y + i + self.hovered, 0, 0, 7)
            
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
                if i == self.choice['hovered']:
                    self.screen.print_at(' ' * max_length, self.x + self.width - max_length, _y + i)
                    self.screen.print_at(element, self.x + self.width - len(element), _y + i)
                else:
                    self.screen.print_at(element, self.x + self.width - len(element), _y + i, 0, 0, 7)
                
        else: # overflow
            for i in range(self.max_listed):
                element_id = i + self.choice['scroll']
                if element_id >= len(pairs): continue
                element_heigth = _y + i
                element = pairs[element_id]['name']
                if element_id == self.choice['hovered']:
                    self.screen.print_at(' ' * max_length, self.x + self.width - max_length, element_heigth)
                    self.screen.print_at(element, self.x + self.width - len(element), element_heigth)
                else:
                    self.screen.print_at(element, self.x + self.width - len(element), element_heigth, 0, 0, 7)
                
            if self.choice['scroll']:
                self.screen.print_at(' ' * max_length, self.x + self.width - max_length, _y, 0, 0, 7)
                self.screen.print_at("△", self.x + self.width - max_length // 2, _y, 0, 0, 7)
            if self.choice['scroll'] != self.choice['number'] - self.max_listed:
                self.screen.print_at(' ' * max_length, self.x + self.width - max_length, _y + self.max_listed - 1, 0, 0, 7)
                self.screen.print_at("▽", self.x + self.width - max_length // 2, _y + self.max_listed - 1, 0, 0, 7)
        
        return
    
    def move_choice_up(self):
        
        self.choice['hovered'] = max(min(self.choice['hovered'] - 1, self.choice['number'] - 1), 0)
        if self.choice['hovered'] < self.choice['scroll'] + 1 and self.choice['scroll'] > 0:
            self.choice['scroll'] -= 1
        
        return
    
    def move_choice_down(self):
        
        self.choice['hovered'] = max(min(self.choice['hovered'] + 1, self.choice['number'] - 1), 0)
        if self.choice['hovered'] > self.max_listed + self.choice['scroll'] - 2 and self.choice["hovered"] != self.choice['number'] - 1: # idk y the second but it works so don't touch
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
            self.screen.print_at(code, 0, 0)
            self.screen.refresh()
            time.sleep(1)
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
            self.update_pair()
            self.selected = False
        return

# TODO:
#   [x] take sources from module Sources
#   [ ] implement fetch process
#   [ ] add graph
#   [ ] add live websocket