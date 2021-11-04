import http.client
import json
import settings

AUTH0_CLIENT_ID = settings.AUTH0_CLIENT_ID
AUTH0_CLIENT_SECRET = settings.AUTH0_CLIENT_SECRET

def getKey():
    conn = http.client.HTTPSConnection("dev-88-mri1m.us.auth0.com")
    payload = "{\"client_id\":\"" + AUTH0_CLIENT_ID + "\",\"client_secret\":\"" + AUTH0_CLIENT_SECRET + "\",\"audience\":\"https://folio.kotkis.fi/\",\"grant_type\":\"client_credentials\"}"
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    access_token = json.loads(data.decode("utf-8"))["access_token"]
    return access_token
