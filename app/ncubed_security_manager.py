import logging, jwt, requests

from authlib.jose import JsonWebKey, jwt as authlib_jwt

from flask_appbuilder.security.sqla.manager import SecurityManager
#from .sec_models import MyUser
#from .sec_views import MyUserDBModelView
log = logging.getLogger(__name__)

class MySecurityManager(SecurityManager):
    def get_oauth_user_info(self, provider, resp):
        # for Authentik
        if provider == 'authentik':
            #log.warn(f'RESPONSE: {resp}')
            id_token = resp["id_token"]
            #log.debug(f"JWT token : {id_token}")
            me = self._decode_jwt(id_token)
            #log.debug(f"Parse JWT token : {me}")
            return {
                "email": me["preferred_username"],
                "first_name": me.get("given_name", ""),
                "username": me["nickname"],
            }
        else:
            return {}

    def _get_jwks(self, jwks_url) -> dict:
        resp = requests.get(jwks_url)
        if resp.status_code == 200:
            return resp.json()
        return False

    def _validate_jwt(self, id_token, jwks):
        keyset = JsonWebKey.import_key_set(jwks)
        claims = authlib_jwt.decode(id_token, keyset)
        claims.validate()
        log.info("JWT token is validated")
        return claims

    def _decode_jwt(self, id_token):
        me = jwt.decode(id_token, options={"verify_signature": False})
        if me.get('iss',''):
            jwks = self._get_jwks(me['iss'] + "jwks/")
            if jwks:
                return self._validate_jwt(id_token, jwks)

        log.warning(f"JWT token is not validated!!!")
        return me
