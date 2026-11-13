from asciimatics.screen import Screen
import render as render
import time

FPS = 20

def main(screen: Screen):
    
    pair = {
        'name': 'BTCUSD',
        'base': 'BTC',
        'quote': 'USD',
        'type': 'Crypto',
        'source': 'biquote'
    }
    
    graph = render.Graph(0, 0, 120, 45, pair, screen)
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
        if not i % int(FPS/2): # twice per second
            graph.fetch_data()
            
        graph.render_frame()
        time.sleep(1 / FPS)
    
    return

Screen.wrapper(main)