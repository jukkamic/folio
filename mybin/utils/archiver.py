from mybin.sources import binance, kucoin, wallets
from mybin.utils import balances
from mybin.serializers import WalletSerializer
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetchStoreWalletData, 'interval', minutes=60)
    scheduler.start()    

def fetchStoreWalletData():
    balances_total = []
    grouped_balances = []
    balances_prices = []
    try:
        balances_total.append(binance.getLendingBalances())
        balances_total.append(binance.getAccountBalances())
        balances_total.append(kucoin.getAccounts())
        balances_total.append(wallets.callEthereum("0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"))
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
    save_wallet_balance(balances_prices)

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


