import hmac, time, requests, hashlib, base64, json
from requests import models
from requests.exceptions import RequestException
from requests.models import Response
from django.conf import settings
from mybin.models import Balance, Coin, Price

API_BASE_URL = 'https://api.kucoin.com'
API_KEY = settings.KUCOIN_API_KEY
API_SECRET = settings.KUCOIN_API_SECRET
API_PASSPHRASE = settings.KUCOIN_API_PASSPHRASE

def getPrice24h(symbol):
    res = call('/api/v1/market/stats', payload={"symbol": symbol + "-USDT"}).json()["data"]
    try:
        price = Price()
        price.coin = Coin(symbol=symbol)
        price.pair = Coin(symbol="USDT")
        price.price = float(res["last"])
        price.source_time = int(res["time"])
        price.recorded_time = int(time.time() * 1000)
        price.change24h = float(res["changeRate"]) * float(100)
        price.chartLink = API_BASE_URL + "/api/v1/market/stats?symbol=" + symbol + "-USDT"
        return price
    except Exception as e:
        print(e)

def getAccounts():
    res = call('/api/v1/accounts').json()["data"]
    balances:Balance = []
    try:
        for balance in res:
            b = Balance()
            b.amount = float(balance["balance"])
            b.coin = Coin(symbol = balance["currency"])
            balances.append(b)
    except Exception as e:
        print(e)
    return balances

def call(endpoint:str, payload:any = None):
    if payload == None:
        payload = {}
    now = int(time.time() * 1000)    
    str_to_sign = str(now) + 'GET' + endpoint
    # for key in payload:
    #     if str_to_sign != "":
    #         str_to_sign = str_to_sign + "&"
    #     str_to_sign = str_to_sign + key + "=" + str(payload[key])
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(API_SECRET.encode('utf-8'), API_PASSPHRASE.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": API_KEY,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }
    try: 
        res = requests.request('get', API_BASE_URL + endpoint, params=payload, headers=headers)
        if res.status_code == requests.codes.ok:
            return res
        else:
            print(res.request.url)
            print(res.json())
            res.raise_for_status()
    except RequestException as e:
        print(e)
        raise Exception("Error fetching from kucoin.", e)
