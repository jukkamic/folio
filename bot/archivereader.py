import http.client
import json
import sys
import auth_util 

def getHistory(days):
    access_token = auth_util.getKey()
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
