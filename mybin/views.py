from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import time
import requests
from requests import status_codes
from requests.exceptions import RequestException
from requests.models import HTTPError
from .sources import binance, wallets
from .utils import balances
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE

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
def getAll(request):
    print("Fetching wallet data.")
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
