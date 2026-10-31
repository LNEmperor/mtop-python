import asyncio, json, websockets, time, data, threading as th
from asciimatics.screen import Screen

async def update_data(graph: data.Graph, stop: th.Event):
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps(SUB))
        while not stop.is_set():
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=0.2)
            except asyncio.TimeoutError:
                continue
            d: dict = json.loads(msg)
            if d.get("type") == "ticker":
                graph.add_data(d)

def main(screen: Screen):
    
    MARKET_GRAPH : data.Graph = data.Graph(screen)
    
    stop = th.Event()
    update = th.Thread(target=(lambda: asyncio.run(update_data(MARKET_GRAPH, stop))))
    update.start()
    
    while True:
        MARKET_GRAPH.render_data()
        time.sleep(FRAME / 1000)
        ev = screen.get_key()
        if ev in [ord('Q'), ord('q')]:
            break
        
    stop.set()
    update.join()
    
    return

if __name__ == "__main__":
    f = open('config.jsonc')
    _data = json.load(f)
    PRODUCT = _data['market']['product']
    FRAME = _data['frame']
    f.close()

    URL = "wss://ws-feed.exchange.coinbase.com"
    SUB = {
        "type": "subscribe",
        "product_ids": [PRODUCT],
        "channels": ["ticker"],
    }
    
    Screen.wrapper(main)