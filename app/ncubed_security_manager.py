import logging
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
            log.debug(str(id_token))
            me = self._azure_jwt_token_parse(id_token)
            log.debug("Parse JWT token : %s", me)
            return {
                "email": me["preferred_username"],
                "first_name": me.get("given_name", ""),
                "username": me["nickname"],
            }
        else:
            return {}