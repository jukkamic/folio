import hmac, time, requests, hashlib

from requests.models import Response

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

def groupBalances(balance_arrays):
    resp = []
    for balance_array in balance_arrays:
        for b in balance_array:
            if not "asset" in b.keys():
                print("asset not in ", b)
                continue
            asset = b["asset"]
            if "amount" in b.keys():
                amount = float(b["amount"])
            elif "free" in b.keys():
                amount = float(b["free"])
                amount += float(b["locked"])
            else:
                print("ERROR: No amount, free or locked fields for asset ", asset)
                raise(KeyError("Could not find fields: amount, free or locked for asset"))
            if (amount > 0):
                # Check if we have the asset already
                addedToResp = False
                for r in resp:
                    if "asset" in r.keys() and r["asset"] == asset:                
                        r_amount = float(r["amount"])
                        resp.append({"asset": asset, "amount": r_amount + amount})
                        addedToResp = True
                if not addedToResp:
                    resp.append({"asset": asset, "amount": amount})
    return resp
