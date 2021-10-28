from django.contrib.auth import authenticate
import json
import jwt
import requests

def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username

def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://dev-88-mri1m.us.auth0.com/.well-known/jwks.json').json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            try:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            except Exception as err:
                print("Error fetching public key: ", err)

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = 'https://dev-88-mri1m.us.auth0.com/'
    try:
        res = jwt.decode(token, public_key, audience='https://folio.kotkis.fi/', issuer=issuer, algorithms=['RS256'])    
        return res
    except Exception as e:
        print(e)