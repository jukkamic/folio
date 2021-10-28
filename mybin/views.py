from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import time
from requests import status_codes
from requests.exceptions import RequestException
from requests.models import HTTPError
from .sources import binance, wallets, kucoin
from .utils import balances
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from functools import wraps
import jwt

# BALANCES_LOCKED = [
#                    {"asset": "ADA", "amount": "21.89281845"},
#                    {"asset": "HNT", "amount": "7.71000000"},
#                    {"asset": "ADA", "amount": "44.36045450"},
#                    {"asset": "ADA", "amount": "30.00000000"},
#                    {"asset": "ALGO", "amount": "109.01983250"}
#                    ]
# BALANCES_KUCOIN = [{"asset": "ETH", "amount": "0.0745"}]
request_times = {}

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope

@csrf_exempt
def testKucoin(request):
    res = kucoin.getAccounts()
    return JsonResponse(data=res, status=HTTP_200_OK, safe=False)
    
@csrf_exempt
def login(request):
    return JsonResponse(data={"token": "test123"}, status=HTTP_200_OK, safe=False)

@csrf_exempt
def getDepositAddr(request, symbol:str):
    res = binance.getDepositAddr(symbol)
    return JsonResponse(data=res.json(), status=res.status_code, safe=False)

@csrf_exempt
def getCustom(request, endpoint:str):
    res = binance.getCustom(endpoint)
    return JsonResponse(data=res.json(), status=res.status_code, safe=False)

@csrf_exempt
def getPrice(request, symbol:str):
    res = binance.getPrice(symbol)
    return JsonResponse(data=res.json(), status=res.status_code, safe=False)

@csrf_exempt
@api_view(['GET'])
@requires_scope('profile')
def getAll(request):
    print("Fetching wallet data.")
    balances_total = []
    grouped_balances = []
    balances_prices = []
    try:
        timeAndAppend(balances_total, "Binance Lending balances", binance.getLendingBalances)
#        timeAndAppend(balances_total, "Binance Liquidity balances", binance.getLiquidityBalances)
        timeAndAppend(balances_total, "Binance Account balances", binance.getAccountBalances)
        timeAndAppend(balances_total, "Kucoin account balances", kucoin.getAccounts)

        start = int(time.time() * 1000)
        balances_total.append(wallets.callEthereum("0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"))
        request_times["Metamask balances"] = int(time.time() * 1000) - start

        # start = int(time.time() * 1000)
        # balances_total.append(wallets.callEthereum("0xe0791977a023213b801a6041305870ec091a40a3"))
        # request_times["Kucoin balances"] = int(time.time() * 1000) - start

  #      balances_total.append(BALANCES_KUCOIN)
 #       balances_total.append(BALANCES_LOCKED)

        # group balances by asset into total
        try:
            grouped_balances = balances.groupBalances(balances_total)
        except Exception as err:
            print(err)
            return JsonResponse(data=err.json(),  status=HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

        # get price info for each asset into prices
        # add prices into total
        start = int(time.time() * 1000)
        for b in grouped_balances:
            asset = b["asset"]
            amount = b["amount"]
            symbol = asset + "USDT"

            priceInfo = None
            if( asset == "TEL" ):
                res = kucoin.getPrice24h(asset)
                price = float(res["last"])
                change = float(res["changeRate"]) * 100
                priceInfo = {"asset": asset, "price": price, "change": change, "value": float(price) * float(amount)}
            if( asset == "USDT" ):
                price = 1
                priceInfo = {"asset": asset, "price": price, "change": "0", "amount": amount, "value": amount}
            if( asset == "BETH" ):
                beth_res = binance.getAllPrices24h("BETHETH").json()
                eth_res = binance.getAllPrices24h("ETHUSDT").json()
                price = float(beth_res["lastPrice"]) * float(eth_res["lastPrice"])
                priceInfo = {"asset": asset, "price": price, "change": beth_res["priceChangePercent"], "value": float(price) * float(amount)} 
            if( not priceInfo ):
                res = binance.getAllPrices24h(symbol)
                price = res.json()["lastPrice"]
                change = res.json()["priceChangePercent"]
                priceInfo = {"asset": asset, "price": price, "change": change, "value": float(price) * float(amount)}
            balances_prices.append(priceInfo)

        request_times["Binance and Kucoin price list"] = int(time.time() * 1000) - start
    except RequestException as err:
        return JsonResponse(data=err.response.json(),  status=HTTP_503_SERVICE_UNAVAILABLE, safe=False)

    printResponseTimes()
    return JsonResponse(data=balances_prices, status=HTTP_200_OK, safe=False)

def timeAndAppend(balances_total, desc:str, fn):
    start = int(time.time() * 1000)
    balances_total.append(fn())
    request_times[desc] = int(time.time() * 1000) - start

def printResponseTimes():
    t = 0
    for r in request_times:
        print(str(r) + " " + str(request_times[r]))
        t = t + request_times[r]
    print("Total requests time:", t)
