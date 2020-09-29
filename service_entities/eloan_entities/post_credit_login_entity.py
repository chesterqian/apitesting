import json
from autotest import BaseServiceEntityHandler
from config.config_handler import config_handler

DOMAIN_NAME = config_handler.creditServiceHost
URL = '%s/api/credit-limit-api-service/login'
BODY_DATA = ''
QUERY_DATA = ''
METHOD_TYPE = 'post'
CONTENT_TYPE = 'json'
REQUEST_DATA = ''
HAS_DATA_PATTERN = False
REQUEST_HEADERS = {
    "X-BK-UUSSSO-Token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsib2F1dGgyLXJlc291cmNlIl0sImFkZGl0aW9uYWxfaW5mbyI6InI1QXVBSXplMWdOOTRLaEw4c3kzMm92ckx0R2lJV2crOW9yeURnVDlWdzB3WWlram1mcEUyS1V0REQ0VS9OdmdHQ054SjdLaVdrM1QrU2thMXdTc0R4QW1xaURUTG43ditDYXFlRFk5aCtENjREUi9LYlo0RFpGcGVEMUNQdkFnTkljaFkyQ1JZRXZ6aFEwaUZhRUxVNDlxNkpPWG5JaGRqT291WmlETnRjZkhsaEorM1dsaFVIaGNXYmRodzVGc2R6WU9TekJ5TldZVk5kNnRXemhrQUdiSXhpWTZUamlNYVRmSGJtV0xsUDlZVTBjMURCWHZBR2kzaEx5NWJYeVEycjRQejlDRUVEZz0iLCJ1c2VyX25hbWUiOiIyMTMxMTAiLCJwYXJ0bmVyX2tleSI6IkJLSksiLCJzY29wZSI6WyJzbnNhcGlfdXNlcmluZm8iLCJzbnNhcGlfcHJpdmF0ZWluZm8iXSwiZXhwIjoxNTUzNjU4NTQ4LCJhdXRob3JpdGllcyI6WyJST0xFX1VTRVIiXSwianRpIjoiOWZkMDdjMzItZGQ2NC00OTRlLTg1OGQtODgwN2JlNGViOWQxIiwiY2xpZW50X2lkIjoiYmtqay0wODIzIn0.dEfPmrNcJc2SKDjRQ6o8s6t7YzCUOIT3ARCBTYH21ZN9JA41nYeKh2nmoncaPM3U8Jupb0WN9jWsXEcZ_ooUGFXAxWDCPo1EzR1-JuvZDNcvTe0WG9dIe0EQ3YgBlKiebgvVu9jTChNBu0huNyCL70YHZ2JLzfWXt2BOnUKnFxX6nOfUfUGIi9dglKKNldmSzJAx7rGvUcnctnQifShjS6EPud3lKF7wmdKkFRl0ffWAyWkssamnVGXkQQQ-LwfyL6m8j-8Vj4ReQfh7YqqDtG0BcaP7QyL4JmZWEFGUcvk-HfgrnlLsHisCHiK1eOqqViDMmn6AVttaZYcJrnx1Aw"}


class PostCreditLoginEntity(BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, domain_name=DOMAIN_NAME, **kwargs):
        super(PostCreditLoginEntity, self).__init__(
            domain_name=domain_name, url_string=URL, data=REQUEST_DATA,
            method_type=METHOD_TYPE, request_content_type=CONTENT_TYPE,
            has_data_pattern=HAS_DATA_PATTERN, request_headers=kwargs.get(
                "request_headers", REQUEST_HEADERS)
        )

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
    e = PostCreditLoginEntity()
    e.send_request()
    print(e.data)
