import asyncio, json, websockets, time, data, threading as th
from asciimatics.screen import Screen

async def update_data(graph : data.Graph):
    async for ws in websockets.connect(URL):
        try:
            await ws.send(json.dumps(SUB))
            async for msg in ws:
                d : dict = json.loads(msg)
                if d.get("type") == "ticker":
                    graph.add_data(d)
        except websockets.ConnectionClosed:
            continue

def main(screen: Screen):
    
    MARKET_GRAPH : data.Graph = data.Graph(screen, 10)
    
    update = th.Thread(target=(lambda: asyncio.run(update_data(MARKET_GRAPH)))) # Error...
    update.start()
    
    while True:
        MARKET_GRAPH.render_data()
        time.sleep(FRAME / 1000)
    
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
        "product_ids": [PRODUCT], # , "BTC-EUR", "ETH-USD", "ETH-EUR"
        "channels": ["ticker"],
    }
    
    Screen.wrapper(main)