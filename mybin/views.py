from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import time
from django.utils import timezone
import pytz
from datetime import datetime, timedelta
from requests import status_codes
from requests.exceptions import RequestException
from requests.models import HTTPError
from .sources import binance, wallets, kucoin
from .utils import balances
from mybin.models import Wallet
from mybin.serializers import WalletSerializer
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from functools import wraps
import jwt
import json

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
                print("Scopes with given token: ", token_scopes)
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope

@csrf_exempt
def getDepositAddr(request, symbol:str):
    res = binance.getDepositAddr(symbol)
    return JsonResponse(data=res.json(), status=res.status_code, safe=False)
    
@csrf_exempt
@api_view(['GET'])           # <-- Need to be authenticated
@requires_scope('read:all')
def getAll(request):
    beth2eth = False
    if (request.query_params.get("beth2eth") == "true"):
        beth2eth = True
    balances_total = []
    grouped_balances = []
    balances_prices = []
    try:
        timeAndAppend(balances_total, "Binance Lending balances", binance.getLendingBalances)
        timeAndAppend(balances_total, "Binance Account balances", binance.getAccountBalances)
        timeAndAppend(balances_total, "Kucoin account balances", kucoin.getAccounts)

        start = int(time.time() * 1000)
        balances_total.append(wallets.callEthereum("0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"))
        request_times["Metamask balances"] = int(time.time() * 1000) - start

        # group balances by asset into total
        try:
            grouped_balances = balances.groupBalances(balances_total)
        except Exception as err:
            print("Error grouping balances", err)
            return JsonResponse(data=err.json(),  status=HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

        # get price info for each asset into prices
        # add prices into total
        start = int(time.time() * 1000)
        try:
            balances_prices = populateBalancesWithPrices(beth2eth, grouped_balances)
        except Exception as e:
            print("Error creating price info. ", e)
            return JsonResponse(data=e.json(),  status=HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

        request_times["Binance and Kucoin price list"] = int(time.time() * 1000) - start
    except RequestException as err:
        print(err)
        return JsonResponse(data=err.response.json(),  status=HTTP_503_SERVICE_UNAVAILABLE, safe=False)

    printResponseTimes()
    return JsonResponse(data=balances_prices, status=HTTP_200_OK, safe=False)

def populateBalancesWithPrices(beth2eth, grouped_balances):
    balances_prices = []
    eth_priceInfo = None
    for b in grouped_balances:
        asset = b.coin.symbol
        amount = b.amount
        symbol = asset + "USDT"

        priceInfo = None
        if( asset == "TEL" ):
            kucoin_res = kucoin.getPrice24h(asset)
            priceInfo = {"asset": asset, "price": kucoin_res.price, "change": kucoin_res.change24h, "value": kucoin_res.price * amount}
        if( asset in ["USDT", "BUSD", "USDC"] ):
            price = 1
            priceInfo = {"asset": asset, "price": price, "change": "0", "amount": amount, "value": amount}
        if( asset == "BETH" ):
            if ( not beth2eth ):
                priceInfo = beth_eth_price(asset, amount, eth_priceInfo) 
            else:
                if (not eth_priceInfo):
                    eth_priceInfo = eth_price("ETH", amount)                 
                priceInfo = {"asset": asset, "price": eth_priceInfo["price"], "change": eth_priceInfo["change"], 
                            "value": eth_priceInfo["value"]}
        if( asset == "ETH" and eth_priceInfo):
            eth_priceInfo["asset"] = asset
            eth_priceInfo["amount"] = amount
            eth_priceInfo["value"] = float(amount) * float(eth_priceInfo["price"])
            priceInfo = eth_priceInfo
        if( not priceInfo ):
            general_res = binance.getAllPrices24h(symbol)
            priceInfo = {"asset": asset, "price": general_res.price, "change": general_res.change24h, "value": float(general_res.price) * float(amount)}
            if (asset == "ETH"):
                eth_priceInfo = priceInfo
        balances_prices.append(priceInfo)
    save_wallet_balance(balances_prices)
    return balances_prices

#@requires_scope('read:all')
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def getBalances(request, days):
    enddate = timezone.now()
    startdate = enddate - timedelta(days=days)
    resp = []
    try:
        res = Wallet.objects.filter(time__range=[startdate, enddate])
        for wallet in res:
            resp.append({"id": wallet.id, "value_usdt": wallet.value_usdt, "btc_usdt": wallet.btc_usdt, "value_btc": wallet.value_btc, "time": str(wallet.time)})        
        return JsonResponse(data=json.dumps(resp), status=HTTP_200_OK, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse(data=json.dumps(e), status=HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

def save_wallet_balance(balances_prices):
    wallet_data = []
    value_usdt = 0
    btc_usdt = 0
    for bp in balances_prices:
        if (bp["asset"] == "BTC"):
            btc_usdt = bp["price"]
        value_usdt += bp["value"]
    wallet_data = {"value_usdt": value_usdt, "btc_usdt": btc_usdt, "value_btc": float(value_usdt) / float(btc_usdt)}
    wallet_serializer = WalletSerializer(data=wallet_data)
    if wallet_serializer.is_valid():
        wallet_serializer.save()
    else:    
        print(wallet_serializer.errors)

def eth_price(asset, amount):
    eth_res = binance.getAllPrices24h("ETHUSDT")
    price = eth_res.price
    priceInfo = {"asset": asset, "price": price, "change": eth_res.change24h, "value": float(price) * float(amount)}
    return priceInfo

def beth_eth_price(asset, amount, eth_priceInfo):
    beth_res = binance.getAllPrices24h("BETHETH")
    if (eth_priceInfo):
        price = beth_res.price * eth_priceInfo["price"]
    else:
        eth_res = binance.getAllPrices24h("ETHUSDT")
        price = beth_res.price * eth_res.price
    priceInfo = {"asset": asset, "price": price, "change": beth_res.change24h, "value": float(price) * float(amount)}
    return priceInfo

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
