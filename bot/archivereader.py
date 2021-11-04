import http.client
import json
import sys

def getKey():
    conn = http.client.HTTPSConnection("dev-88-mri1m.us.auth0.com")
    payload = "{\"client_id\":\"BAPLSqjMGzr3u9TQc8pAiQLtQC2bovqI\",\"client_secret\":\"1k8KDIEzm_r9-uWlvRarTh3DXz1rX1aMXHa7msxwd4c4P-SO2HAuGNHeh7RecFKe\",\"audience\":\"https://folio.kotkis.fi/\",\"grant_type\":\"client_credentials\"}"
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    access_token = json.loads(data.decode("utf-8"))["access_token"]
    return access_token


def getHistory(days):
    access_token = getKey()
    conn = http.client.HTTPSConnection("folio.kotkis.fi")
    headers = { 'authorization': "Bearer " + access_token}
    conn.request("GET", "/folio/wallet/history/" + days + "/", headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(json.loads(data.decode("utf-8")))

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 2 and args[0] == '-days':
        getHistory(args[1])
    else:
        print("Arguments: -days <number>")
