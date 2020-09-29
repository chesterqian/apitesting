import json
from autotest import BaseServiceEntityHandler

from config.config_handler import config_handler

DOMAIN_NAME = config_handler.credLoanapiHost
URL = '%s/withdraw-apply/{}/latest-loan'
BODY_DATA = ''
_BODY_DATA = ''
if BODY_DATA:
    _BODY_DATA = json.loads(BODY_DATA)
QUERY_DATA = ''
METHOD_TYPE = 'get'
CONTENT_TYPE = ''
REQUEST_DATA = _BODY_DATA or QUERY_DATA
REQUEST_HEADERS = (
    [{'name': 'X-UID', 'value': '213110'},
     {'name': 'cache-control', 'value': 'no-cache'},
     {'name': 'Postman-Token',
      'value': 'f2ed559e-233c-4326-b271-da5df1cae850'},
     {'name': 'User-Agent', 'value': 'PostmanRuntime/7.6.1'},
     {'name': 'Accept', 'value': '*/*'},
     {'name': 'Host', 'value': 'cred-loanapi.dev.bkjk.cn'},
     {'name': 'accept-encoding', 'value': 'gzip, deflate'},
     {'name': 'Connection', 'value': 'keep-alive'}]
)
HAS_DATA_PATTERN = False


class GetWithdrawApplyEloanSalaryLatestLoanEntity(
    BaseServiceEntityHandler):
    """
    accessible attribute list for response data:
    %s
    ==================
    kwargs for request:
    Please refer to the constants BODY_DATA or QUERY_DATA request parameters
    """

    def __init__(self, domain_name=DOMAIN_NAME, loan_type="ELOAN_SALARY",
                 **kwargs):
        super(GetWithdrawApplyEloanSalaryLatestLoanEntity, self).__init__(
            domain_name=domain_name, url_string=URL.format(loan_type),
            data=REQUEST_DATA, method_type=METHOD_TYPE, 
            request_content_type=CONTENT_TYPE,
            request_headers=kwargs.get("request_headers", REQUEST_HEADERS),
            has_data_pattern=HAS_DATA_PATTERN)


if __name__ == '__main__':
    e = GetWithdrawApplyEloanSalaryLatestLoanEntity()
    e.send_request()
    print(e.productId)
