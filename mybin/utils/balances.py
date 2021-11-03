from mybin.models import Balance, Coin
from mybin.sources import binance, kucoin

SMALL_BALANCE = 10

def getPriceFromList(symbol:str, allPrices:any):
    for p in allPrices.json():
        if p["symbol"] == symbol:
            return p
    return {}

def filterSmallBalances(balances):
    balances_response = []
    for b in balances:
        if b["value"] > SMALL_BALANCE:
            balances_response.append(b)
    return balances_response

def getAssetFromList(symbol, balances):
    for b in balances:
        try:
            if b.coin.symbol == symbol:
                return b
        except Exception as e:
            print("Error at balance " + str(b), e)
    return None        

def groupBalances(balance_arrays):
    grouped_balances:Balance = []
    for balance_array in balance_arrays:
        for asset in balance_array:
            symbol = asset.coin.symbol
            amount = asset.amount
            if (amount > 0):
                added_asset = getAssetFromList(symbol, grouped_balances)
                if added_asset:
                    added_asset.amount += amount
                else:
                    grouped_balances.append( Balance( coin=Coin( symbol=symbol ), amount=amount ) )
    return grouped_balances

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
    return balances_prices

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
