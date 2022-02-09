import hmac, time, requests, hashlib
from requests.exceptions import RequestException
from requests.models import Response
from django.conf import settings
from django.core import serializers

from mybin.models import Balance, Coin, Price

# ISOLATED MARGIN ACCOUNT RESPONSE
# {
# "assets": [
# {
# "baseAsset": {
# "asset": "BTC",
# "borrowEnabled": true,
# "borrowed": "0",
# "free": "0.00112887",
# "interest": "0",
# "locked": "0",
# "netAsset": "0.00112887",
# "netAssetOfBtc": "0.00112887",
# "repayEnabled": true,
# "totalAsset": "0.00112887"
# },
# "quoteAsset": {
# "asset": "USDT",
# "borrowEnabled": true,
# "borrowed": "0",
# "free": "150.07886",
# "interest": "0",
# "locked": "0",
# "netAsset": "150.07886",
# "netAssetOfBtc": "0.00339779",
# "repayEnabled": true,
# "totalAsset": "150.07886"
# },
# "symbol": "BTCUSDT",
# "isolatedCreated": true,
# "marginLevel": "999",
# "marginLevelStatus": "EXCESSIVE",
# "marginRatio": "10",
# "indexPrice": "44168.56313279",
# "liquidatePrice": "0",
# "liquidateRate": "0",
# "tradeEnabled": true,
# "enabled": true
# },

API_KEY = settings.BINANCE_API_KEY
API_SECRET = settings.BINANCE_API_SECRET
BASE_URL = "https://api.binance.com"
ACCOUNT_URL = "/api/v3/account"
LENDING_URL = "/sapi/v1/lending/union/account"
ISOLATED_URL = "/sapi/v1/margin/isolated/account"
FIXED_URL = "/sapi/v1/lending/project/position/list"
LIQUIDITY_URL = "/sapi/v1/bswap/liquidity"
DIVIDEND_URL = "/sapi/v1/asset/assetDividend"
ACTIVITY_URL = "/sapi/v1/lending/project/list"
PURCHASE_URL = "/sapi/v1/lending/union/purchaseRecord"
PRICE_URL = "/api/v3/ticker/price"
PRICE24_URL = "/api/v3/ticker/24hr"
# symbol lastPrice priceChangePercent
SAVINGS_URL = "/sapi/v1/lending/daily/product/list"
TOKEN_LENDING_URL = "/sapi/v1/lending/daily/token/position"
GET_DEPOSIT_ADDR = "/sapi/v1/capital/deposit/address"

def getDepositAddr(symbol:str):
    payload = {"coin": symbol}
    try:
        res = call(GET_DEPOSIT_ADDR, payload)
    except Exception as e:
        print(e)
        raise("Could not fetch deposit address for coin " + symbol, e)
    return res
         
def getLiquidityBalances():
    balances = []
    pools = call(LIQUIDITY_URL).json()
    for pool in pools:
        shareAmount = float(pool["share"]["shareAmount"])
        if shareAmount > 0:
            for key in pool["share"]["asset"]:
                balances.append({"asset": key, "amount": float(pool["share"]["asset"][key])})
    return balances

def getDividend():
    return call(DIVIDEND_URL).json()["rows"]

def getAccountBalances():
    res = call(ACCOUNT_URL).json()["balances"]
    balances:Balance = []
    try:
        for balance in res:
            b = Balance()
            b.coin = Coin(symbol = balance["asset"])
            b.amount = float(balance["free"])
            b.amount += float(balance["locked"])
            if( b.amount > 0 ):
                balances.append(b)
    except Exception as e:
        print(e)
    return balances

def getLendingBalances():
    res = call(LENDING_URL).json()["positionAmountVos"]
    balances:Balance = []
    try:
        for balance in res:
            b = Balance()
            b.coin = Coin(symbol = balance["asset"])
            b.amount = float(balance["amount"])
            if( b.amount > 0 ):
                balances.append(b)
    except Exception as e:
        print(e)
    return balances

def getPrice(symbol:str):
    return requests.get(BASE_URL + PRICE_URL, params={"symbol": symbol})

def getAllPrices():
    return requests.get(BASE_URL + PRICE_URL)

def getAllPrices24h(symbol):
    res = requests.get(BASE_URL + PRICE24_URL, params={"symbol": symbol}).json()
    price = Price()
    price.change24h = float(res["priceChangePercent"])
    price.price = float(res["lastPrice"])
    return price

def call(endpoint:str, payload:any = None):
    if payload == None:
        payload = {}
    timestamp = int(time.time() * 1000)    
    payload["timestamp"] = str(timestamp)
    q = ""
    for key in payload:
        if q != "":
            q = q + "&"
        q = q + key + "=" + str(payload[key])
    m = hmac.new(API_SECRET.encode("utf-8"), q.encode('utf-8'), hashlib.sha256)
    signature = m.hexdigest()
    payload["signature"] = signature
    try: 
        res = requests.get(BASE_URL + endpoint, 
            params=payload,
            headers={'X-MBX-APIKEY': API_KEY}) 
        if res.status_code == requests.codes.ok:
            return res
        else:
            print(res.request.url)
            print(res.json())
            res.raise_for_status()
    except RequestException as e:
        print(e)
        raise Exception("Error fetching from binance.", e)
