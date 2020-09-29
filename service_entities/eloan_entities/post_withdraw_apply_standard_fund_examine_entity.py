import json
from autotest import BaseServiceEntityHandler
from config.config_handler import config_handler

DOMAIN_NAME = config_handler.credLoanapiHost
URL = '%s/withdraw-apply/{}/standard-fund-examine'
BODY_DATA = ''
_BODY_DATA = ''
if BODY_DATA:
    _BODY_DATA = json.loads(BODY_DATA)
QUERY_DATA = ''
METHOD_TYPE = 'post'
CONTENT_TYPE = 'json'
REQUEST_DATA = ''
REQUEST_HEADERS = (
    [{'name': 'X-UID', 'value': '213109'},
     {'name': 'cache-control', 'value': 'no-cache'},
     {'name': 'Postman-Token',
      'value': '9d695c26-890d-4a11-9a7b-4fc71ad5917a'},
     {'name': 'User-Agent', 'value': 'PostmanRuntime/7.6.1'},
     {'name': 'Accept', 'value': '*/*'},
     {'name': 'Host', 'value': 'cred-loanapi.dev.bkjk.cn'},
     {'name': 'accept-encoding', 'value': 'gzip, deflate'},
     {'name': 'content-length', 'value': '0'},
     {'name': 'Connection', 'value': 'keep-alive'}]
)
HAS_DATA_PATTERN = False


class PostWithdrawApplyStandardFundExamineEntity(BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, domain_name=DOMAIN_NAME, apply_id=1, **kwargs):
        super(PostWithdrawApplyStandardFundExamineEntity, self).__init__(
            domain_name=domain_name, url_string=URL.format(apply_id), data=REQUEST_DATA,
            method_type=METHOD_TYPE, request_content_type=CONTENT_TYPE,
            has_data_pattern= HAS_DATA_PATTERN, request_headers=kwargs.get(
                             "request_headers", REQUEST_HEADERS
                         ))

    def _set_data_pattern(self, *args, **kwargs):
        pass
                                                                
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
    e = PostWithdrawApplyStandardFundExamineEntity()
    e.send_request()
