import hmac, time, requests, hashlib
from requests.models import Response
from django.conf import settings

API_KEY = settings.BINANCE_API_KEY
API_SECRET = settings.BINANCE_API_SECRET
BASE_URL = "https://api.binance.com"
ACCOUNT_URL = "/api/v3/account"
LENDING_URL = "/sapi/v1/lending/union/account"
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

urlMap = {
        "liquidity": LIQUIDITY_URL,            
        "lending": LENDING_URL,
        "account": ACCOUNT_URL,
        "fixed": FIXED_URL,
        "dividend": DIVIDEND_URL,
        "activity": ACTIVITY_URL,
        "purchase": PURCHASE_URL,
        "savings": SAVINGS_URL,
        "token": TOKEN_LENDING_URL,
        }
         
def getCustom(endpoint:str):
    print ("Endpoint", endpoint)
    url = ""
    if endpoint in urlMap:
        url = urlMap[endpoint]
    else:
        res = Response()
        print( "Endpoint " + endpoint + " not defined.")
        res._content = b'{"message": "Endpoint not defined"}'
        return res
    try:
        payload = {}
        if endpoint == "activity":
            payload = {"type": "ACTIVITY"}
        if endpoint == "purchase":
            payload = {"lendingType": "ACTIVITY"}
            """
            "DAILY" for flexible, "ACTIVITY" for activity, "CUSTOMIZED_FIXED" for fixed
            """
        res = call(url, payload)
        return res
    except AttributeError as aErr:
        print(aErr)
    except:
        print("Unknown error fetching from Binance API")

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
    return call(ACCOUNT_URL).json()["balances"]

def getLendingBalances():
    return call(LENDING_URL).json()["positionAmountVos"]

def getPrice(symbol:str):
    return requests.get(BASE_URL + PRICE_URL, params={"symbol": symbol})

def getAllPrices():
    return requests.get(BASE_URL + PRICE_URL)

def getAllPrices24h(symbol):
    return requests.get(BASE_URL + PRICE24_URL, params={"symbol": symbol})

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
    res = requests.get(BASE_URL + endpoint, 
        params=payload,
        headers={'X-MBX-APIKEY': API_KEY}) 
    if res.status_code == requests.codes.ok:
        return res
    else:
        print(res.request.url)
        print(res.json())
        res.raise_for_status()
