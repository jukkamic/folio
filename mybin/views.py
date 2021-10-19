from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import time
import requests
from requests.models import HTTPError
from .sources import binance, wallets
from .utils import balances
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

# BALANCES_LOCKED = [
#                    {"asset": "ADA", "amount": "21.89281845"},
#                    {"asset": "HNT", "amount": "7.71000000"},
#                    {"asset": "ADA", "amount": "44.36045450"},
#                    {"asset": "ADA", "amount": "30.00000000"},
#                    {"asset": "ALGO", "amount": "109.01983250"}
#                    ]
# BALANCES_KUCOIN = [{"asset": "ETH", "amount": "0.0745"}]
request_times = {}

@csrf_exempt
def getCustom(request, endpoint:str):
    res = binance.getCustom(endpoint)
    return JsonResponse(data=res.json(), status=res.status_code, safe=False)

@csrf_exempt
def getPrice(request, symbol:str):
    res = binance.getPrice(symbol)
    return JsonResponse(data=res.json(), status=res.status_code, safe=False)

@csrf_exempt
def getAll(request):
    hideSmall = request.GET.get('hideSmall')
    if not hideSmall:
        hideSmall="false"
    balances_total = []
    grouped_balances = []
    balances_prices = []
    try:
        timeAndAppend(balances_total, "Binance Lending balances", binance.getLendingBalances)
#        timeAndAppend(balances_total, "Binance Liquidity balances", binance.getLiquidityBalances)
        timeAndAppend(balances_total, "Binance Account balances", binance.getAccountBalances)

        start = int(time.time() * 1000)
        balances_total.append(wallets.callEthereum("0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"))
        request_times["Metamask balances"] = int(time.time() * 1000) - start

        # start = int(time.time() * 1000)
        # balances_total.append(wallets.callEthereum("0xe0791977a023213b801a6041305870ec091a40a3"))
        # request_times["Kucoin balances"] = int(time.time() * 1000) - start

  #      balances_total.append(BALANCES_KUCOIN)
 #       balances_total.append(BALANCES_LOCKED)


        # group balances by asset into total
        grouped_balances = balances.groupBalances(balances_total)

        # get price info for each asset into prices
        # add prices into total
        start = int(time.time() * 1000)
        for b in grouped_balances:
            asset = b["asset"]
            amount = b["amount"]
            symbol = asset + "USDT"

            priceInfo = None
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

        request_times["Binance price list"] = int(time.time() * 1000) - start
    except HTTPError as err:
        return JsonResponse(data=err.response.json(),  status=HTTP_503_SERVICE_UNAVAILABLE, safe=False)

    if hideSmall.lower()=="true":
        balances_filtered = balances.filterSmallBalances(balances_prices)
    printResponseTimes()
    return JsonResponse(data=balances_filtered, status=HTTP_200_OK, safe=False)

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

@csrf_exempt
def mockAll(request):
    mockData = {
        "LUNA": {
            "amount": 7.23494866,
            "price": 36.93,
            "value": 267.18665401379997
        },
        "ETH": {
            "amount": 0.04334374,
            "price": 2945.35,
            "value": 127.66248460899999
        },
        "FRONT": {
            "amount": 110,
            "price": 1.1361,
            "value": 124.97100000000002        
        },
        "XTZ": {
            "amount": 13.29471207,
            "price": 6.063,
            "value": 80.60583928041
        },
        "ENJ": {
            "amount": 59.37579733,
            "price": 1.272,
            "value": 75.52601420376
        },
        "BTC": {
            "amount": 0.0041872,
            "price": 42501.83,
            "value": 177.96366257600002
        },
        "BNB": {
            "amount": 0.00046694,
            "price": 340.2,
            "value": 0.158852988
        },
        "USDT": {
            "amount": 9.985863,
            "price": 1,
            "value": 9.985863
        },
        "ADA": {
            "amount": 74.5371471,
            "price": 2.154,
            "value": 160.5530148534
        },
        "ATOM": {
            "amount": 2.9058123,
            "price": 37.3,
            "value": 108.38679878999999
        },
        "ALGO": {
            "amount": 109.21678331000001,
            "price": 1.6992,
            "value": 185.58115820035204
        }
    }
    return JsonResponse(data=mockData, status=HTTP_200_OK, safe=False)
