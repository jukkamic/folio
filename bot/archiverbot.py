import http.client
import json
import auth_util 

def storeData():
    access_token = auth_util.getKey()
    conn = http.client.HTTPSConnection("folio.kotkis.fi")
    headers = { 'authorization': "Bearer " + access_token}
    conn.request("GET", "/folio/wallet/history/store/", headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

if __name__ == "__main__":
    storeData()
