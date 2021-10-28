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

def getAssetFromList(symbol, assets):
    for a in assets:
        try:
            if a["asset"] == symbol:
                return a
        except Exception as e:
            print("Error at asset " + str(a), e)
    return None

def groupBalances(balance_arrays):
    resp = []
    for balance_array in balance_arrays:
        for asset in balance_array:
            if not "asset" in asset.keys() and not "currency" in asset.keys():
                print("asset or currency not in ", asset)
                continue
            if "asset" in asset.keys():
                symbol = asset["asset"]
            else:
                symbol = asset["currency"]
            if "amount" in asset.keys():
                amount = float(asset["amount"])
            elif "balance" in asset.keys():
                amount = float(asset["balance"])
            elif "free" in asset.keys():
                amount = float(asset["free"])
                amount += float(asset["locked"])
            else:
                print("ERROR: No amount, balance, free or locked fields for asset ", symbol)
                raise(KeyError("Could not find fields: amount, free or locked for asset"))
            if (amount > 0):
                added_asset = getAssetFromList(symbol, resp)
                if added_asset:
                    added_asset["amount"] = added_asset["amount"] + amount
                else:
                    resp.append({"asset": symbol, "amount": amount})
    return resp
