import http.client
import json

def getKey():
    conn = http.client.HTTPSConnection("dev-88-mri1m.us.auth0.com")
    payload = "{\"client_id\":\"BAPLSqjMGzr3u9TQc8pAiQLtQC2bovqI\",\"client_secret\":\"1k8KDIEzm_r9-uWlvRarTh3DXz1rX1aMXHa7msxwd4c4P-SO2HAuGNHeh7RecFKe\",\"audience\":\"https://folio.kotkis.fi/\",\"grant_type\":\"client_credentials\"}"
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    access_token = json.loads(data.decode("utf-8"))["access_token"]
    return access_token

def storeData():
    access_token = getKey()
    conn = http.client.HTTPSConnection("folio.kotkis.fi")
    headers = { 'authorization': "Bearer " + access_token}
    conn.request("GET", "/folio/wallet/history/store/", headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

if __name__ == "__main__":
    storeData()
