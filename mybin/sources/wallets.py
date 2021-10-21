import requests
from django.conf import settings
from requests.exceptions import RequestException

def callAlgo():
    balances = []
    res = requests.get("https://algoexplorerapi.io/v2/accounts/U67IYL7HW3P4Q3BFBM3UUABXHXCJ472N3I7ORAR2OP4XKCRBYF6ENG6TCQ")
    if res.status_code == requests.codes.ok:
        res_json = res.json()
        amount = float(float(res_json["amount"]) / 1000000)
        balances = [{"asset": "ALGO", "amount": amount}]
        return balances
    else:
        print(res.json()["msg"])
        res.raise_for_status()

def callEthereum(address:str):
    FETCH_CONTRACT = "0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85"
    balances = []
    payload = {}
    payload["module"] = "account"
    payload["action"] = "balance"
    payload["address"] = address
    #"0x8065EaCe34ab4c5df020893e13d5A42eE7675D93"
    payload["tag"] = "latest"
    payload["apikey"] = settings.ETHERSCAN_API_KEY
    res = requests.get("https://api.etherscan.io/api", params=payload)
    if res.status_code == requests.codes.ok:
        res_json = res.json()
        if res_json["status"] == "1":
            billion = int(1000000000)
            wei = int(res_json["result"])
            eth = float(wei / billion / billion)
            balances = [{"asset": "ETH", "amount": str(eth)}]
            token_balances = getErc20Txs(address, FETCH_CONTRACT)
            for tb in token_balances:
                balances.append(tb)
            return balances
    print(res.json()["message"])
    res.raise_for_status()

def getErc20Txs(address:str, contract:str):
    print("Fetching tokens")
    payload = {}
    payload["module"] = "account"
    payload["action"] = "tokentx"
    payload["contractAddress"] = contract
    payload["address"] = address
    payload["startblock"] = "13049017"
    payload["apikey"] = settings.ETHERSCAN_API_KEY
    try:
        res = requests.get("https://api.etherscan.io/api", params=payload)
    except RequestException as e:
        print(e)
        raise(e)
    if res.status_code == requests.codes.ok:
        token_balances = {}
        resp = []
        res_json = res.json()
        if res_json["status"] == "1":
            billion = int(1000000000)
            for result in res_json["result"]:
                sign = 1 if result["to"] == address else -1
                token = result["tokenSymbol"]
                val = float(result["value"]) / billion / billion
                if token in token_balances.keys():
                    token_balances[token] = str( float(token_balances[token]) + sign * val )
                else:
                    token_balances[token] = str(val)
            for b in token_balances.keys():
                resp.append({"asset": b, "amount": str(token_balances[b])})
            return resp
    print(res.json()["message"])
    res.raise_for_status()
    
def callTerra():
    balances = []
    res = requests.get("https://lcd.terra.dev/bank/balances/terra1m87j29xmfacl5k9l7pfp4xgx2dvcgkl95azda4")
    if res.status_code == requests.codes.ok:
        res_json = res.json()
        for item in res_json["result"]:
            if item["denom"] == "uluna":
                amount = float(float(item["amount"]) / 1000000)
                balances = [{"asset": "LUNA", "amount": amount}]
            elif item["denom"] == "luna":
                amount = float(item["amount"])
                balances = [{"asset": "LUNA", "amount": amount}]
            else:
                amount = 0
        return balances
    else:
        print(res.json()["msg"])
        res.raise_for_status()
