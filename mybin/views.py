from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import time
from django.utils import timezone
from zoneinfo import ZoneInfo
from datetime import timedelta, tzinfo
from .sources import binance, wallets, kucoin
from .utils import balances
from mybin.models import Wallet
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from functools import wraps
import jwt
import json

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
    request_times = {}
    try:
        request_times = timeAndAppend(request_times, balances_total, "Binance Lending balances", binance.getLendingBalances)
        request_times = timeAndAppend(request_times, balances_total, "Binance Account balances", binance.getAccountBalances)
        request_times = timeAndAppend(request_times, balances_total, "Kucoin account balances", kucoin.getAccounts)

        start = int(time.time() * 1000)
        balances_total.append(wallets.callEthereum("0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"))
        request_times["Metamask balances"] = int(time.time() * 1000) - start

        try:
            grouped_balances = balances.groupBalances(balances_total)
        except Exception as err:
            print("Error grouping balances", err)
            return JsonResponse(data=json.dumps(err),  status=HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

        start = int(time.time() * 1000)
        try:
            balances_prices = balances.populateBalancesWithPrices(beth2eth, grouped_balances)
        except Exception as e:
            print("Error creating price info. ", e)
            return JsonResponse(data=json.dumps(e),  status=HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

        request_times["Binance and Kucoin price list"] = int(time.time() * 1000) - start
    except Exception as err:
        print("Exception ", err)
        return JsonResponse(data=err.response.json(),  status=HTTP_503_SERVICE_UNAVAILABLE, safe=False)

    printResponseTimes(request_times)
    return JsonResponse(data=balances_prices, status=HTTP_200_OK, safe=False)

#@requires_scope('read:all')
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def getBalances(request, days):
    enddate = timezone.now(tzinfo=ZoneInfo("Europe/Helsinki"))
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

def timeAndAppend(request_times, balances_total, desc:str, fn):
    start = int(time.time() * 1000)
    balances_total.append(fn())
    request_times[desc] = int(time.time() * 1000) - start
    return request_times

def printResponseTimes(request_times):
    t = 0
    for r in request_times:
        print(str(r) + " " + str(request_times[r]))
        t = t + request_times[r]
    print("Total requests time:", t)
