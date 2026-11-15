import fetchSources as Sources
import requests as rq
import datetime

"""import threading as th
import json

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect"""

"""def fetch_live_data(stop: th.Event):
    while not stop.is_set():
        try:
            with connect(URL) as ws:
                ws.send(json.dumps(SUB))
                while not stop.is_set():
                    try:
                        msg = ws.recv(timeout=0.5)
                    except TimeoutError:
                        continue
                    d = json.loads(msg)
                    if d.get("type") == "ticker":
                        ticks.put(d)
        except (ConnectionClosed, OSError):
            stop.wait(1)  """
            
def fetch_biquote(name: str):
    
    raw = rq.get(Sources.SOURCES['biquote'][1] + name).json()
    result = {
        'value': float(raw['mid']),
        'time': datetime.datetime.strptime(raw['time'], '%Y.%m.%d %T')
    }
    
    return result

def fetch_coinbase(name: str):
    
    raw = rq.get(Sources.SOURCES["coinbase"][1] + name + '/spot').json()
    result = {
        'value': float(raw['data']['amount']),
        'time': datetime.datetime.now()
    }
    
    return result

def fetch_binance(name: str):
    
    raw = rq.get(Sources.SOURCES["binance"][1] + '?symbol=' + name + '&limit=1').json()
    result = {
        'value': (float(raw['bids'][0][0]) + float(raw['asks'][0][0])) / 2, # avgPrice only updates every 5 mins so order book is better
        'time': datetime.datetime.now()
    }
    
    return result

def fetch_kraken(name: str):
    
    raw = rq.get(Sources.SOURCES["kraken"][1] + "?pair=" + name).json()
    result = {
        'value': float(raw['result'][name]['c'][0]),
        'time': datetime.datetime.now()
    }
    
    return result

def fetch(source: str, name: str):

    funcs = {
        'biquote': fetch_biquote,
        'coinbase': fetch_coinbase,
        'binance': fetch_binance,
        'kraken': fetch_kraken
    }

    return funcs[source](name)

# print(fetch_binance('BTCUSD'))
# print(fetch_kraken('0GEUR'))