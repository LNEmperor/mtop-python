from asciimatics.screen import Screen
import json

def render(OHCL, height, screen: Screen, x_pos=0, y_pos=0, data_max=None, data_min=None):
    if data_max is not None and data_min is not None:
        _max = data_max
        _min = data_min
    else:
        _max = OHCL['high']
        _min = OHCL['low']

    if _max == _min:               # flat market, avoid step = 0
        _max += 1
        _min -= 1

    step = (_max - _min) / height
    rise = OHCL['open'] <= OHCL['close']
    top = max(OHCL['open'], OHCL['close'])
    bot = min(OHCL['open'], OHCL['close'])
    color = Screen.COLOUR_GREEN if rise else Screen.COLOUR_RED

    for i in range(height):
        level = _max - i * step
        if level >= OHCL['high']:
            continue
        elif level >= top:
            screen.print_at('│', x_pos, y_pos+i + 1, color)
        elif level >= bot:
            screen.print_at(' ', x_pos, y_pos+i + 1, bg=color)
        elif level >= OHCL['low']:
            screen.print_at('│', x_pos, y_pos+i + 1, color)


def render_data(screen: Screen, data):
    
    with open('config.jsonc', 'r') as f:
        config = json.load(f)
        f.close()
        
    dx : int = config['market']['x']
    y : int = config['market']['y']
    
    height : int = config['market']['height']
    width : int = config['market']['width'] - 15
        
    candles = [
        c
        for _, c in sorted(data.items(), key=lambda kv: int(kv[0]))
        if isinstance(c, dict) and c   # skip raw/empty
    ]
    if not candles:
        return

    candles = candles[-width:]
    data_max = max(c['high'] for c in candles)
    data_min = min(c['low'] for c in candles)
    
    mid = True
    start = candles[0]['open']
    rise = candles[0]['open'] <= candles[-1]['close']
    
    if data_max != data_min:
        s_step = int((height - 2) * (start - data_min) / (data_max - data_min))
    else:
        mid = False
        
    screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)
    
    render_box(screen, data_max, data_min)
    
    if mid:
        screen.print_at("-" * width, dx + 1, s_step, Screen.COLOUR_GREEN if rise else Screen.COLOUR_RED) # to check (feels like s_step if wrong)

    for x, ohlc in enumerate(candles):
        render(ohlc, height-2, screen, dx+x+1, y-1, data_max, data_min)
    screen.refresh()
    
def render_box(screen: Screen, data_max : float, data_min : float):
    
    with open('config.jsonc', 'r') as f:
        config = json.load(f)
        f.close()
        
    x : int = config['market']['x']
    y : int = config['market']['y']
    
    height : int = config['market']['height']
    width : int = config['market']['width']
    
    product : str = config['market']['product']
    rounded : bool = config['boxes']['rounded']
    
    color : int = config['boxes']['color']
    
    # # # # Box
    
    void_fill : str = " " * (width - 2)
    bar_fill : str = "─" * (width - 2)
    
    top : str = "┌" if not rounded else "╭"
    fill : str = "─" * ((width - 8) // 2)
    top += fill + "Market" + fill
    top += "─" if len(fill)%2 != width%2 else ""
    top += "┐" if not rounded else "╮"
    
    screen.print_at(top, x, y, color)
    
    for i in range(1, height - 1):
        screen.print_at("│" + void_fill + "│", x, y+i, color)
    
    corner_l : str = "└" if not rounded else "╰"
    corner_r : str = "┘" if not rounded else "╯"
    
    screen.print_at(corner_l + bar_fill + corner_r, x, y+height-1, color)
    
    # # # # Product
    
    screen.print_at(product, x + width - len(product) - 2, y + 1)
    
    # # # # Scale
    
    step = (data_max - data_min) / (height - 2)
    
    for i in range(1, height-1):
        if not i%3:
            screen.print_at(f"- {(data_max - step*i):,.2f}", x + width - 14, y + i)
    
    return