import json
from autotest import BaseServiceEntityHandler
from config.config_handler import config_handler

DOMAIN_NAME = config_handler.credLimitapiHost
URL = '%s/credit-limit?'
BODY_DATA = ''
_BODY_DATA = ''
if BODY_DATA:
    _BODY_DATA = json.loads(BODY_DATA)
QUERY_DATA = 'productId=ELOAN_SALARY'
METHOD_TYPE = 'get'
CONTENT_TYPE = ''
REQUEST_DATA = ''
REQUEST_HEADERS = (
    [{'name': 'X-UID', 'value': '213109'}, {'name': 'X-BK-UUSSSO-Token',
                                            'value': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsib2F1dGgyLXJlc291cmNlIl0sImFkZGl0aW9uYWxfaW5mbyI6InI1QXVBSXplMWdOOTRLaEw4c3kzMm92ckx0R2lJV2crOW9yeURnVDlWdzB3WWlram1mcEUyS1V0REQ0VS9OdmdHQ054SjdLaVdrM1QrU2thMXdTc0R4QW1xaURUTG43ditDYXFlRFk5aCtENjREUi9LYlo0RFpGcGVEMUNQdkFnTkljaFkyQ1JZRXZ6aFEwaUZhRUxVNDlxNkpPWG5JaGRqT291WmlETnRjZkhsaEorM1dsaFVIaGNXYmRodzVGc2R6WU9TekJ5TldZVk5kNnRXemhrQUdiSXhpWTZUamlNYVRmSGJtV0xsUDlZVTBjMURCWHZBR2kzaEx5NWJYeVEycjRQejlDRUVEZz0iLCJ1c2VyX25hbWUiOiIyMTMxMTAiLCJwYXJ0bmVyX2tleSI6IkJLSksiLCJzY29wZSI6WyJzbnNhcGlfdXNlcmluZm8iLCJzbnNhcGlfcHJpdmF0ZWluZm8iXSwiZXhwIjoxNTUzNTkzOTM3LCJhdXRob3JpdGllcyI6WyJST0xFX1VTRVIiXSwianRpIjoiOGJmNjVjNjEtYjcyNi00ODg0LWE3NjEtODQ4ZTIyNjM5ZDk5IiwiY2xpZW50X2lkIjoiYmtqay0wODIzIn0.cObSmYscv6gtOFaim-5M9-6Pp1r-0ltg4XadLLic85ue8hOq-lvLpmy8I1_I9tkVlLO_GdYOc5JBd9AYe8VIeLnGotTpQy-jKsz1B-V3XL5N0Mwp1XbCMjhQ1MXAi7zshzZ8CdYsEI0l9Ff9EMJ2SbGltwN6eNXpgGE6L99V5-3juYmxBqhzkoOWBLMDYA-vY5p5qWhtFbOiZw4riiiGj9z6ScnLFPLcfqtvR8LOmX3NK60YvzA4P2Psoiw7s3tDCzBIrdnyJ24nBlYg1UlFP1d-BSUIbXvj6MEiZ0ipciw5IuXhj5r2I6CE-oZedXhBsY7zwdJijWwcniljelU4Dg'},
     {'name': 'cache-control', 'value': 'no-cache'},
     {'name': 'Postman-Token',
      'value': '73518658-8a76-48a0-abd4-009b44e74a58'},
     {'name': 'User-Agent', 'value': 'PostmanRuntime/7.6.1'},
     {'name': 'Accept', 'value': '*/*'},
     {'name': 'Host', 'value': 'cred-limitapi.dev.bkjk.cn'},
     {'name': 'accept-encoding', 'value': 'gzip, deflate'},
     {'name': 'Connection', 'value': 'keep-alive'}]
)
HAS_DATA_PATTERN = True


class GetCreditLimitEntity(BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, domain_name=DOMAIN_NAME, **kwargs):
        super(GetCreditLimitEntity, self).__init__(domain_name=domain_name,
                                                   url_string=URL,
                                                   data=REQUEST_DATA,
                                                   method_type=METHOD_TYPE,
                                                   request_content_type=CONTENT_TYPE,
                                                   has_data_pattern=HAS_DATA_PATTERN,
                                                   request_headers=kwargs.get(
                                                       "request_headers",
                                                       REQUEST_HEADERS)
                                                   )

    def _set_data_pattern(self, *args, **kwargs):
        self._current_data_pattern = QUERY_DATA

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
    e = GetCreditLimitEntity()
    e.send_request(productId="ELOAN_SALARY1")
    def getNum(num):
        if num > 1:
            return num * getNum(num - 1)
        else:
            return num


    print(getNum(4))


    def first_way(a, b):
        while (b != 0):
            temp = a % b
            a = b
            b = temp

        return a


    print(first_way(8, 16))

