from asciimatics.screen import Screen
import render as render
import time
import json

DEFAULT_CONFIG = {
    "market": {
        "product": "ETH-USD",
        "height": 30,
        "width": 100,
        "x": 0,
        "y": 0,
        "slice": 10
    },
    "boxes": {
        "rounded": True
    },
    "fps": 20
}

def main(screen: Screen):

    try:
        open('config.jsonc')
    except FileNotFoundError:
        f = open('config.jsonc', 'x')
        json.dump(DEFAULT_CONFIG, f)
        f.close()

    with open('config.jsonc') as f:
        data = json.load(f)
        FPS = data['fps']
    
    default_pair = { # TODO change
        'name': 'BTCUSD',
        'base': 'BTC',
        'quote': 'USD',
        'type': 'Crypto',
        'source': 'biquote'
    }
    
    graph = render.Graph(0, 0, default_pair, screen)
    graph.render_frame()
    i = 0
    
    while True:
        ev = screen.get_key()
        if ev:
            if ev == -204: #up
                graph.key_up()
            elif ev == -206: # down
                graph.key_down()
            elif ev == 10: # enter
                graph.key_enter()
            else:
                if graph.key(ev):
                    break
        
        i += 1
        if not i % int(FPS / 2): # twice per second
            graph.fetch_data()
            graph.render_frame()

        graph.render_frame()
        time.sleep(1 / FPS)
    
    return

Screen.wrapper(main)