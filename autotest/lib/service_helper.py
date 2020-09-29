# -*- coding: utf-8 -*-
import json

import requests

from autotest.global_config import Global
from autotest.exception import BadStatusCodeException

CONTENT_TYPE_DICTIONARY = {
    'form': Global.HeaderContentType.FORM,
    'json': Global.HeaderContentType.JSON
}
CONTENT_TYPE_MAP_DATA_KWARGS = {
    'form': 'data',
    'json': 'json'
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

    @staticmethod
    def _build_headers(content_type=None, cookies=None, token=None, request_headers=None):
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12'}

        if content_type:
            _headers.update({"Content-Type": content_type})

        if cookies:
            _headers.update({"Cookie": dump_cookies(cookies)})

        if token:
            _headers.update({"token": token})

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
        data = domain_name
        if not data:
            raise Exception("domain_name should be supplied !")
        url = service_url_pattern % data

        return url

    def call_service_with_post(self, url_pattern, data,
                               content_type='form', cookies=None,
                               domain_name=None, token=None, request_headers=None, request_timeout=None):
        url = self._build_service_url(url_pattern, domain_name)
        headers = self._build_headers(CONTENT_TYPE_DICTIONARY[content_type], cookies, token,
                                      request_headers=request_headers)
        data_kwarg = CONTENT_TYPE_MAP_DATA_KWARGS[content_type]
        response = self.sessions.post(url, headers=headers, verify=False, timeout=request_timeout, **{data_kwarg: data})
        self.verify_status_code(response, url, {"headers": headers, "verify": False,
                                                "timeout": request_timeout, "data": data})

        return response

    def call_service_with_get(self, url_pattern, data='',
                              cookies=None, domain_name=None,
                              token=None, stream=False, request_headers=None, request_timeout=None):
        url = self._build_service_url(url_pattern, domain_name)
        headers = self._build_headers(cookies=cookies, token=token, request_headers=request_headers)
        parameters = {'url': url + data, 'headers': headers, 'timeout': request_timeout}
        # data is dict
        # response = self.sessions.get(url, params=data, headers=headers, verify=False)
        response = self.sessions.get(verify=False, stream=stream, **parameters)
        self.verify_status_code(response, url, parameters)

        return response

    def call_service_with_delete(self, url_pattern, data='',
                                 cookies=None, domain_name=None,
                                 token=None, request_headers=None, request_timeout=None):
        url = self._build_service_url(url_pattern, domain_name)
        headers = self._build_headers(cookies=cookies, token=token, request_headers=request_headers)
        parameters = {'url': url + data, 'headers': headers, 'timeout': request_timeout}
        response = self.sessions.delete(verify=False, **parameters)
        self.verify_status_code(response, url, parameters)

        return response

    def call_service_with_put(self, url_pattern, data, content_type='form',
                              cookies=None, domain_name=None,
                              token=None, request_headers=None, request_timeout=None):
        headers = self._build_headers(CONTENT_TYPE_DICTIONARY[content_type], cookies, token,
                                      request_headers=request_headers)
        url = self._build_service_url(url_pattern, domain_name)
        data_type = CONTENT_TYPE_MAP_DATA_KWARGS[content_type]
        parameters = {'url': url, data_type: data, 'headers': headers, 'timeout': request_timeout}
        response = self.sessions.put(**parameters)
        self.verify_status_code(response, url, parameters)

        return response

    def call_service_with_multipart_post(self, url_pattern, data,
                                         files, cookies=None,
                                         domain_name=None, token=None, request_headers=None, request_timeout=None):
        url = self._build_service_url(url_pattern, domain_name)
        headers = self._build_headers(cookies=cookies, token=token, request_headers=request_headers)
        response = self.sessions.post(url, data=data, files=files, headers=headers, timeout=request_timeout,
                                      verify=False)
        self.verify_status_code(response, url, {"data": data, "files": files, "headers": headers,
                                                "timeout": request_timeout, "verify": False})

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
