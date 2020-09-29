import json
from autotest import BaseServiceEntityHandler
from config.config_handler import config_handler

DOMAIN_NAME = config_handler.credLoanapiHost
URL = '%s/withdraw-apply/{}/upload-file?applyId={}&fileType={}'
BODY_DATA = ''
QUERY_DATA = ''
METHOD_TYPE = 'multipart_post'
CONTENT_TYPE = 'form'
REQUEST_DATA = ''
REQUEST_HEADERS = {}

HAS_DATA_PATTERN = False


class PostWithdrawApplyUploadFileEntity(BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, file_name, apply_id,
                file_type="LOAN_PURPOSE_CERTIFICATION", 
                files=None,
                domain_name=DOMAIN_NAME, 
                **kwargs):
        super(PostWithdrawApplyUploadFileEntity, self).__init__(
                             domain_name=domain_name, 
                             url_string=URL.format(file_name, apply_id, file_type), 
                             data=REQUEST_DATA, 
                             method_type=METHOD_TYPE, 
                             request_content_type=CONTENT_TYPE, 
                             has_data_pattern=HAS_DATA_PATTERN, 
                             request_headers=kwargs.get("request_headers",
                                                        REQUEST_HEADERS),
                             files=files)

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
    from util import intersection_of_path
    relative_path = "test-eloan/tests/service_entities_unit_test/static/ddt_upsert_withdraw_apply.json"
    file_path = intersection_of_path(relative_path)

    with open(file_path, 'rb')as f:
        files = {"file": (f.name, f)}
        e = PostWithdrawApplyUploadFileEntity(1, 1, files=files)
        e.send_request()

