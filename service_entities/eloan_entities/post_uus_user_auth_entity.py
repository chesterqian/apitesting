import json
from autotest import BaseServiceEntityHandler
from config.config_handler import config_handler

DOMAIN_NAME = config_handler.apiHost
URL = '%s/uus/user/auth'
BODY_DATA = '''
            {
              "accountName": "13083933483",
              "accountType": "PHONE",
              "authType": "CODE",
              "clientId": "bkjk-0823",
              "clientSecret": "MrQx28VIOfCtFQXjf4teDqQFMntrjjEp",
              "deviceInfo": {
                "appIP": "",
                "appMAC": "",
                "appVersion": "280",
                "channel": "BKJK",
                "deviceFingerPrint": "",
                "deviceId": "865132034031752",
                "os": "",
                "osVersion": "",
                "source": ""
              },
              "grantType": "password",
              "inviteCode": "",
              "inviteType": "",
              "partnerKey": "BKJK",
              "partnerUID": "",
              "password": "666666",
              "verifyToken": ""
            }
            '''
QUERY_DATA = ''
METHOD_TYPE = 'post'
CONTENT_TYPE = 'json'
REQUEST_DATA = ''
REQUEST_HEADERS = {}
HAS_DATA_PATTERN = True


class PostUusUserAuthEntity(BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, domain_name=DOMAIN_NAME, **kwargs):
        super(PostUusUserAuthEntity, self).__init__(domain_name=domain_name,
                                                    url_string=URL,
                                                    data=REQUEST_DATA,
                                                    method_type=METHOD_TYPE,
                                                    request_content_type=CONTENT_TYPE,
                                                    has_data_pattern=HAS_DATA_PATTERN,
                                                    request_headers=kwargs.get(
                                                        "request_headers",
                                                        REQUEST_HEADERS))

    def _set_data_pattern(self, *args, **kwargs):
        self._current_data_pattern = BODY_DATA

    def _handle_data_before_request(self):
        """
            The method can help add extra fields or modify fields in request before sending, for example sign field.
            Access method:
                self._data is the form or json body(type dict) for put/post requests or query string(type str) for get requests.
                self._request_headers is http headers (type [{'name':'', 'value':''}])
                self.cookies is http cookies (type RequestsCookieJar)
            For example, to add sign field for post form body, you can write code:
                sign = lib.sign.signature(self._data)
                self._data['sign'] = sign
        """
        pass


if __name__ == '__main__':
    e = PostUusUserAuthEntity()
    e.send_request(accountName="13083933483",
                   clientSecret="MrQx28VIOfCtFQXjf4teDqQFMntrjjEp",
                 )

    print(e.access_token)
