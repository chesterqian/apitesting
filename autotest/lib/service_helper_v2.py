# -*- coding: utf-8 -*-
import json

import requests

from autotest.global_config import Global
from autotest.exception import BadStatusCodeException

CONTENT_TYPE_DICTIONARY = {
    'form': Global.HeaderContentType.FORM,
    'json': Global.HeaderContentType.JSON,
    'text': "text/html"
}
CONTENT_TYPE_MAP_DATA_KWARGS = {
    'form': 'data',
    'json': 'json',
    "default": "data"
}


def dump_cookies(cookies):
    cookie_string = ""

    for cookie in cookies:
        if type(cookies) is list:
            cookie_string += cookie['name'] + "=" + cookie['value'] + ";"
        else:
            "type(cookies) is instance"
            cookie_string += cookie.name + "=" + cookie.value + ";"

    return cookie_string


class Singleton(type):
    _instances = {}

    def __call__(cls, *args):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args)
        return cls._instances[cls]


class ServiceHelper(object):
    def __init__(self):
        self.sessions = requests.Session()
        self.Http_Method_Map = {
            "post": self.sessions.post,
            "get": self.sessions.get,
            "put": self.sessions.put,
            "delete": self.sessions.delete,
            "multipart_post": self.sessions.post,
        }

    def do_request(self, method, **kwargs):
        assert method
        method_exec = self.Http_Method_Map[method]
        response = method_exec(**kwargs)
        return response

    @staticmethod
    def _build_headers(content_type=None, cookies=None, token=None, request_headers=None):
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12'}

        if content_type:
            _headers.update({"Content-Type": content_type})

        if cookies:
            _headers.update({"Cookie": dump_cookies(cookies)})

        if token:
            _headers.update({"Authorization": token})

        if request_headers:
            if isinstance(request_headers, list):
                for i in request_headers:
                    _headers.update({i['name']: i['value']})
            elif isinstance(request_headers, dict):
                _headers.update(request_headers)
            else:
                raise Exception('require list or dict!')

        return _headers

    @staticmethod
    def _build_service_url(service_url_pattern, domain_name=None):
        if not domain_name:
            raise Exception("domain_name should be supplied !")
        url = service_url_pattern % domain_name

        return url

    def call_service(self, method, url_pattern, body_data="", params=None,
                     content_type='json', files=None,
                     cookies=None, domain_name=None,
                     token=None, request_headers=None,
                     request_timeout=None, verify=False):
        headers = self._build_headers(
            content_type=CONTENT_TYPE_DICTIONARY.get(
                content_type, CONTENT_TYPE_DICTIONARY["text"]),
            cookies=cookies,
            token=token,
            request_headers=request_headers)
        url = self._build_service_url(url_pattern, domain_name)
        data_type = CONTENT_TYPE_MAP_DATA_KWARGS.get(
            content_type, CONTENT_TYPE_MAP_DATA_KWARGS["default"])
        parameters = {'url': url,
                      'params': params,
                      data_type: body_data,
                      'headers': headers,
                      "files": files,
                      'timeout': request_timeout,
                      'verify': verify}
        response = self.do_request(method, **parameters)
        self.verify_status_code(response, url, parameters)

        return response

    @staticmethod
    def verify_status_code(response, url, request=None):
        if response.status_code not in (200, 201):
            request_str = request if request else ''
            if isinstance(request, dict):
                try:
                    request_str = json.dumps(request, ensure_ascii=False, indent=4)
                except Exception as e:
                    pass
            msg = 'The response error is encountered(%s), ' \
                  'url:%s\n' \
                  'request:\n%s\n' \
                  'response:\n%s.' % (
                    response.status_code, url, request_str, response.text)
            raise BadStatusCodeException(msg, response)


class ServiceHelperSingleton(ServiceHelper, metaclass=Singleton):
    pass
