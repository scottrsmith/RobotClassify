#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json

import http.client
import config
from jose import jwt
from urllib.request import urlopen


# API_PATH = 'http://127.0.0.1:5000/'

# ----------------------------------------------------------------------------#
# helper functions
# ----------------------------------------------------------------------------#
def dumpObj(obj, name='None'):
    print('\n\nDump of object...{}'.format(name))
    for attr in dir(obj):
        print("    obj.%s = %r" % (attr, getattr(obj, attr)))


def verify_decode_jwt(token):

    unverified_header = jwt.get_unverified_header(token)
    jsonurl = \
        urlopen(f'https://dev-p35ewo73.auth0.com/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    rsa_key = {}

    if 'kid' not in unverified_header:
        raise AuthError({'code': 'invalid_header',
                        'description': 'Authorization malformed.'}, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
                }
    if rsa_key:
        try:
            payload = jwt.decode(token, rsa_key,
                                 algorithms=config.ALGORITHMS,
                                 audience=config.AUTH0_AUDIENCE,
                                 issuer='https://' + config.AUTH0_DOMAIN + '/')
            return payload
        except jwt.ExpiredSignatureError:
            abort(401, 'Token expired.')
        except jwt.JWTClaimsError:
            abort(401,
                  'Incorrect claims. Please, check the audience and issuer.'
                  )
        except Exception:
            abort(400, 'Unable to parse authentication token.')

    abort(400, 'Unable to find the appropriate key.')


conn = http.client.HTTPSConnection(config.AUTH0_DOMAIN)
payload = "{\"client_id\":\"" +\
          config.AUTH0_CLIENT_ID +\
          "\",\"client_secret\":\"" +\
          config.AUTH0_CLIENT_SECRET +\
          "\",\"audience\":\"" + config.AUTH0_AUDIENCE +\
          "\",\"grant_type\":\"client_credentials\"}"

headers = {'content-type': "application/json"}
conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = json.loads(res.read().decode("utf-8"))
token = data['access_token']

payload = verify_decode_jwt(token)
userid = payload['sub']

print('APP_TESTING_USERID={}'.format(userid))
print('TOKEN={}'.format(token))
