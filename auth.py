import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'dev-p35ewo73.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'robotclassify'


# Auth Header

# def get_token_auth_header():
#   raise Exception('Not Implemented')

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """

    auth = request.headers.get('Authorization', None)
    if not auth:
        abort(401, 'Authorization header is expected.')

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        abort(401, 'Authorization header must start with "Bearer".')
    elif len(parts) == 1:

        abort(401, 'Token not found.')
    elif len(parts) > 2:

        abort(401, 'Authorization header must be bearer token.')

    token = parts[1]
    return token


# ----------------------------------------------------------------------------#
#  Raise an AuthError if permissions are not included in the payload
#
#  INPUTS
#     permission: string permission (i.e. 'post:admin')
#        payload: decoded jwt payload
# ----------------------------------------------------------------------------#

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400, 'Permissions not included in JWT.')

    if permission not in payload['permissions']:
        abort(401, 'Permission not found.')

    return True


# ----------------------------------------------------------------------------#
# verify_decode_jwt(token) method
# INPUTS
#    token: a json web token (string)
# Returns:
#     decoded payload
# ----------------------------------------------------------------------------#

def verify_decode_jwt(token):
    jsonurl = urlopen('https://' + AUTH0_DOMAIN + '/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
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
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')

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


# ----------------------------------------------------------------------------#
#  @requires_auth(permission) decorator method
#  INPUTS
#     permission: string permission (i.e. 'post:admin')
#
# ----------------------------------------------------------------------------#

def requires_auth(permission=''):
    print ('enter requires_auth')
    def requires_auth_decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except Exception:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper

    return requires_auth_decorator
