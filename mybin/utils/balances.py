from mybin.models import Balance, Coin

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
