import requests as rq
import json

BINANCE_LIST    = "https://api.binance.com/api/v3/exchangeInfo"
BINANCE_URL     = "https://api.binance.com/api/v3/depth" # + f"?symbol={name}"
BINANCE_WSS     = "wss://stream.binance.com:9443/ws/" # + f"{name}@avgPrice"

COINBASE_LIST   = "https://api.exchange.coinbase.com/products"
COINBASE_URL    = "https://api.coinbase.com/v2/prices/" # + f"{name}/spot"
COINBASE_WSS    = None # TODO find

KRAKEN_LIST     = "https://api.kraken.com/0/public/AssetPairs"
KRAKEN_URL      = "https://api.kraken.com/0/public/Ticker" # + f"?pair={name}"
KRAKEN_WSS      = "wss://ws.kraken.com/v2"

# BITSTAMP_LIST   = "https://bitstamp.net/api/v2/trading-pairs-info/"
# BITSTAMP_WSS    = "wss://ws.bitstamp.net"

# BITFINEX_LIST   = "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange"
# BITFINEX_WSS    = "wss://api-pub.bitfinex.com/ws/2"

BIQUOTE_LIST    = "https://biquote.io/api/symbols"
BIQUOTE_URL     = "https://biquote.io/api/" # + name
BIQUOTE_WSS     = None

SOURCES = {
    "binance": [BINANCE_LIST, BINANCE_URL, BINANCE_WSS],
    "coinbase": [COINBASE_LIST, COINBASE_URL, COINBASE_WSS],
    "kraken": [KRAKEN_LIST, KRAKEN_URL, KRAKEN_WSS],
    # "bitstamp": [BITSTAMP_LIST, BITSTAMP_URL],
    # "bitflex": [BITFINEX_LIST, BITFINEX_URL]
    "biquote": [BIQUOTE_LIST, BIQUOTE_URL, BIQUOTE_WSS]
}

def fetch_list_from(source: str):
    
    data_f =  open('data/data.json')
    data : dict = json.load(data_f)
    data_f.close()
        
    if data[source]:
        with open(f'data/{source}.json') as f:
            return json.load(f)
        
    else:
        with open(f'data/{source}.json', 'x') as f:
            raw = rq.get(SOURCES[source][0])
            formatted = json.loads(raw.text)
            
            if source == 'binance':
                
                formatted = list(map(
                    lambda a: {
                        "name": a["symbol"],
                        "base": a["baseAsset"],
                        "quote": a["quoteAsset"],
                        "type": "Crypto",
                        'source': 'binance'
                    },
                    formatted['symbols']
                ))
                
            elif source == 'coinbase':
                
                formatted = list(map(
                    lambda a: {
                        "name": a['id'],
                        "base": a["base_currency"],
                        "quote": a["quote_currency"],
                        "type": "Crypto",
                        'source': 'coinbase'
                    },
                    formatted
                ))
                
            elif source == 'biquote':
                
                formatted = list(map(
                    lambda a: {
                        "name": a['name'],
                        "base": a["currency"],
                        "type": a['type'],
                        "quote": a["name"] if a["type"] == "Stock" else list(filter(
                            lambda a: a != '',
                            a["name"].split(a['currency'])
                        ))[0],
                        'source': 'biquote'
                    },
                    formatted
                ))
                
            elif source == 'kraken':
                
                formatted = list(map(
                    lambda a: {
                        "name": formatted['result'][a]['altname'],
                        "base": formatted['result'][a]['base'],
                        "quote": formatted['result'][a]['wsname'].split('/')[1],
                        "type": "Unknown",
                        'source': 'kraken'
                    },
                    formatted['result']
                ))
            
            json.dump(formatted, f, indent=4)
        
        data[source] = True
        data_f = open('data/data.json', 'w')
        json.dump(data, data_f, indent=4)
        data_f.close()
        return formatted
    
def get_pairs_from_quote(source: str, quote: str):
    
    all_pairs = fetch_list_from(source)
    quotes = list(filter(
        lambda a: a['quote'] == quote,
        all_pairs
    ))
    
    return quotes

def get_all_pairs_from_quote(quote: str):
    
    quotes = {}
    for i in SOURCES:
        quotes[i] = get_pairs_from_quote(i, quote)
    
    return quotes

def get_pairs_from_base(source: str, base: str):
    
    all_pairs = fetch_list_from(source)
    bases = list(filter(
        lambda a: a['base'] == base,
        all_pairs
    ))
    
    return bases

def get_all_pairs_from_base(base: str):
    
    bases = {}
    for i in SOURCES:
        bases[i] = get_pairs_from_base(i, base)
    
    return bases

if __name__ == "__main__":
    get_all_pairs_from_base('USD') # loads all sources