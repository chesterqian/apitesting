# -*- coding: utf-8 -*-
import json
from autotest import BaseServiceEntityHandler

DOMAIN_NAME = ''
URL = 'http://%s/restful_service_generator'
BODY_DATA = ''
_BODY_DATA = ''
if BODY_DATA:
    _BODY_DATA = json.loads(BODY_DATA)
QUERY_DATA = ''
METHOD_TYPE = 'post'
CONTENT_TYPE = 'json'
REQUEST_DATA = _BODY_DATA or QUERY_DATA
REQUEST_HEADERS = ''
HAS_DATA_PATTERN = False


class CodeGenServiceEntity(BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, data, domain_name=DOMAIN_NAME):
        super(CodeGenServiceEntity, self).__init__(
            domain_name=domain_name,
            url_string=URL,
            data=data,
            method_type=METHOD_TYPE,
            request_content_type=CONTENT_TYPE,
            request_headers=REQUEST_HEADERS,
            has_data_pattern=HAS_DATA_PATTERN
        )

    def _set_data_pattern(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    e = CodeGenServiceEntity()
    e.send_request()
