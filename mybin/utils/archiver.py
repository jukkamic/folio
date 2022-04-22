from mybin.sources import binance, kucoin, wallets
from mybin.utils import balances
from mybin.serializers import WalletSerializer
import http.client
import json

# def start():
#     scheduler = BackgroundScheduler(timezone="Europe/Helsinki")
#     scheduler.add_job(fetchStoreWalletData, 'interval', minutes=60)
#     scheduler.start()    

def fetchStoreWalletData():
    balances_total = []
    grouped_balances = []
    balances_prices = []
    try:
#        balances_total.append(binance.getLendingBalances())
        balances_total.append(binance.getAccountBalances())
        balances_total.append(kucoin.getAccounts())
        balances_total.append(wallets.callEthereum("0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"))
#        balances_total.append(wallets.callAlgo())
        try:
            grouped_balances = balances.groupBalances(balances_total)
        except Exception as err:
            print("Error grouping balances", err)
        try:
            balances_prices = balances.populateBalancesWithPrices(False, grouped_balances)
        except Exception as e:
            print("Error creating price info. ", e)
    except Exception as err:
        print(err)
    _save_wallet_balance(balances_prices)

def _save_wallet_balance(balances_prices):
    wallet_data = []
    value_usdt = 0

    conn = http.client.HTTPSConnection("folio.kotkis.fi")
#    conn = http.client.HTTPConnection("localhost:8000")
    conn.request("GET", "/folio/wallet/price/BTCUSDT/")
    res = conn.getresponse()
    data = res.read()
    response_json = json.loads(data.decode("utf-8"))
    btc_usdt = response_json["price"]

    for bp in balances_prices:
        value_usdt += bp["value"]
    try:
        wallet_data = {"value_usdt": value_usdt, "btc_usdt": btc_usdt, "value_btc": float(value_usdt) / float(btc_usdt)}
        wallet_serializer = WalletSerializer(data=wallet_data)
    except Exception as err:
        print(err)
    if wallet_serializer.is_valid():
        wallet_serializer.save()
    else:    
        print("Error serializing wallet. ", wallet_serializer.errors)


