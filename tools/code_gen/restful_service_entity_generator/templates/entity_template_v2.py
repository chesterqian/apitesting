import json
# from autotest.base_service_entity_handler_v2 import BaseServiceEntityHandler
from autotest import BaseServiceEntityV2 as BaseServiceEntity
DOMAIN_NAME = 'http://127.0.0.1:5000'
URL = '%s/tasks?'
BODY_DATA = ''
QUERY_DATA = ''
METHOD_TYPE = 'post'
CONTENT_TYPE = 'json'
REQUEST_HEADERS = ""


class PostTasksEntity(BaseServiceEntity):
    def __init__(self, **kwargs):
        super(PostTasksEntity, self).__init__(
            domain_name=kwargs.get('domain_name', DOMAIN_NAME),
            url_string=URL.format(),
            body_data=kwargs.get('body_data', BODY_DATA),
            query_string=kwargs.get('query_string', QUERY_DATA),
            has_data_pattern=kwargs.get('has_data_pattern', True),
            method_type=METHOD_TYPE,
            request_content_type=CONTENT_TYPE,
            request_headers=kwargs.get('request_headers', REQUEST_HEADERS))

    def _handle_body_data_before_request(self):
        """
            The method can help add extra fields or modify fields in request before sending,
            for example sign field.
            Access method:
                self._body_data is the request body(type dict).
                self._query_string is the request query string
                self._request_headers is http headers (format: [{'name':'Token','value':'1234567890'}])
                self.cookies is http cookies (type RequestsCookieJar)
            For example, to add sign field for post form body, you can write code:
                sign = lib.sign.signature(self._data)
                self._data['sign'] = sign
        """
        pass

    def _transform_response_body_to_dict(self, response_body):
        '''
        The method can help solve parsing non-json response body.
        If need, entity class should customize this function.
        :parameter: the response_body: requests.response.content
        :return:  the dict transformed from your own response body
        '''
        return self._body_data


if __name__ == '__main__':
    e = PostTasksEntity()
    e.set_query_parameters()
    e.send_request()
    print(e.json_content)
