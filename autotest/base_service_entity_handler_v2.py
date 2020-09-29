# -*- coding:utf-8 -*-
import copy
import inspect
import json
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import re
from .lib.service_helper_v2 import ServiceHelper
from .lib.json_handler import handle_item_in_json, set_field_value
from .meta_data_handler import BaseMetaDataHandler
from .utility import Utility
from .exception import BadStatusCodeException


class EntityMetaClass(type):
    def __new__(cls, name, bases, attrs):
        attrs['utility'] = Utility()
        return super(EntityMetaClass, cls).__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        cls._service_helper = 'service_helper' in kwargs and \
                              kwargs[
                                  'service_helper'] or ServiceHelper()

        [kwargs.pop(key) for key in ('service_helper',) if
         key in kwargs]
        return super(EntityMetaClass, cls).__call__(*args, **kwargs)


class BaseServiceEntity(object, metaclass=EntityMetaClass):
    def __init__(self, url_string=None, body_data=None, query_string='',
                 files=None, method_type='get', has_data_pattern=True,
                 request_content_type='json', domain_name=None,
                 cookies=None,
                 token=None, stream=False, request_headers=None,
                 request_timeout=None, data=None):
        self._url_string = url_string
        self._body_data = body_data
        self._data = self._body_data
        self._has_data_pattern = has_data_pattern
        self._request_content_type = request_content_type
        self._domain_name = domain_name
        self._method_type = method_type
        self._files = files
        self._default_url_pattern = url_string
        self._default_body_data = body_data
        self._query_string = query_string
        self._default_request_content_type = request_content_type
        self._default_method_type = method_type
        self._json_content = None
        self._response = None
        self.cookies = cookies
        self._token_in_header = token
        self.stream = False
        if request_headers and isinstance(request_headers, str):
            request_headers = json.loads(request_headers)
        self._request_headers = request_headers
        self._request_timeout = request_timeout
        self._special_node_attributes = []
        self._special_key_attributes = []
        # 将类变量赋给实例变量
        self.service_helper = self._service_helper

        # compatible with v1
        if self._has_data_pattern:
            if "_set_data_pattern" in dir(self):
                self._set_data_pattern()
            if not body_data and self._current_data_pattern and method_type == "post":
                self._body_data = self._current_data_pattern
            if not query_string and self._current_data_pattern and method_type == "get":
                self._query_string = self._current_data_pattern
        else:
            if not body_data and data and method_type == "post":
                self._body_data = data
                self._has_data_pattern = False
            if not query_string and data and method_type == "get":
                self._query_string = data
                self._has_data_pattern = False

        self._delete_fields = list()
        self._send_request_kwargs = None
        self._response_meta_data = None
        self._body_data_meta_handler = None
        self._query_string_meta_handler = None
        self.update_body_data_meta_handler()
        self.update_query_string_meta_handler()

    def update_body_data_meta_handler(self):
        if not self._has_data_pattern:
            return
        body_data = self._body_data
        if not body_data:
            self._body_data_meta_handler = None
            return
        if isinstance(body_data, str):
            body_data = json.loads(body_data)
        self._body_data_meta_handler = BaseMetaDataHandler(body_data)

    def update_query_string_meta_handler(self):
        if not self._has_data_pattern:
            return
        query_string = self._query_string
        if not query_string:
            self._query_string_meta_handler = None
            return
        if isinstance(query_string, str):
            queries = dict()
            kv_search = re.findall(r"([A-Za-z0-9_-\{\}]+)=([A-Za-z0-9_-\{\}]+)",
                                   query_string)
            for k, v in kv_search:
                queries[k] = v
            query_string = queries
        if not isinstance(query_string, dict):
            raise Exception(
                "query_string format error, {}".format(query_string))
        self._query_string = query_string
        self._query_string_meta_handler = BaseMetaDataHandler(query_string)

    @property
    def json_content(self):
        return self._json_content

    @property
    def response_content(self):
        if not self._response:
            self._request()

        return self._response

    @property
    def response_meta_data(self):
        if not self._response_meta_data:
            if self._json_content:
                self._response_meta_data = \
                    BaseMetaDataHandler(self._json_content)

        return self._response_meta_data

    def _refresh_default_args(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _request(self):
        self._response = None
        self._json_content = None
        self._response_meta_data = None

        try:
            params = self._query_string
            body_data = self._body_data

            if self._has_data_pattern:
                if self._query_string_meta_handler:
                    params = self._query_string_meta_handler.meta_data
                if self._body_data_meta_handler:
                    body_data = self._body_data_meta_handler.meta_data

            parameters = {
                "method": self._method_type,
                "domain_name": self._domain_name,
                "url_pattern": self._url_string,
                "body_data": body_data,
                "params": params,
                "content_type": self._request_content_type,
                "cookies": self.cookies,
                "token": self._token_in_header,
                "request_headers": self._request_headers,
                "request_timeout": self._request_timeout,
                "files": self._files
            }
            self._response = self.service_helper.call_service(**parameters)

        except BadStatusCodeException as e:
            self._response = e.response
            self._handle_response()
            raise e

        if self._response:
            self._handle_response()
        return self._response

    def _handle_response(self):
        try:
            self._json_content = self._response.json()
        except ValueError:
            self._json_content = self._transform_response_body_to_dict(
                self._response.content)
        if self._request_content_type in ["json", "form"]:
            self._response_meta_data = BaseMetaDataHandler(self._json_content)

        self.cookies = self._response.cookies

    def update_response_json(self, json_content):
        self._json_content = json_content
        self._response_meta_data = BaseMetaDataHandler(self._json_content)

    def _reload(self):
        self._url_string, self._body_data, self._method_type = \
            self._default_url_pattern, self._default_body_data, \
            self._default_method_type

        self._request()

    def _save_send_request_kwargs(self, kwargs):
        self._send_request_kwargs = kwargs

    def set_delete_fields(self, delete_list):
        self._delete_fields = delete_list

    def _delete_fields_as_required(self):
        def delete_in_dict(d, items):
            '''
            delete field in a dict
            '''
            data = d
            for i, f in enumerate(items):
                if i == len(items) - 1:
                    del data[items[i]]
                else:
                    data = data[items[i]]

        if not self._request_content_type in ["json", "form"]:
            return

        for field in self._delete_fields:
            split_field = field.split(".")
            delete_in_dict(self._body_data, split_field)

    def _handle_data_before_request(self):
        """
        The method can help add extra fields or modify fields in request before sending, for example sign field. 
        Access method:  
            self._body_data is the form or json body(type dict) for put/post requests or query string(type str) for get requests.
            self._request_headers is http headers (type [{'name':'', 'value':''}])
            self.cookies is http cookies (type RequestsCookieJar)
        For example, to add sign field for post form body, you can write code:
            sign = lib.sign.signature(self._body_data)
            self._body_data['sign'] = sign
        """
        pass

    def _transform_response_body_to_dict(self, response_body):
        '''
        The method can help solve parsing non-json response body. If need, entity class should customize this function.
        :parameter: the response_body , type str
        :return:  the dict transformed from your own response body
        '''
        return self._body_data

    def set_request_data(self, data):
        self._has_data_pattern = False
        self._body_data = data

    def get_request_data(self):
        return self._body_data

    def __getattr__(self, attribute):
        """
        The method can help to get the entity attribute value in json object.
        And no declaration is needed in the entity.
        There are some requirements have to meet for the attribute name:
        i. the name should be combined with 'node name'+'_'+'key name' of the attribute in json object;
        ii. if 'node name' includes '_', the attribute name has to be added in special_node_attributes.
        iii. if 'key name' includes '_', the attribute name has to be added in special_key_attributes.
        :param attribute: the attribute name
        :return: the value which is corresponding to the given attribute name in json object.
        """
        if not (self._response or self._json_content):
            return None
        values = getattr(self.response_meta_data, attribute)

        return values

    def update_partial_query_data(self, partial_query_data):
        self._body_data = self._default_body_data + partial_query_data
        self._request()

        return self

    def send_request(self, **kwargs):
        self._set_body_data_handler(**kwargs)
        self._handle_data_before_request()
        if self._delete_fields:
            self._delete_fields_as_required()

        return self._request()

    def _set_body_data_handler(self, **kwargs):
        if not self._has_data_pattern or not self._body_data_meta_handler:
            return
        for k, v in kwargs.items():
            setattr(self._body_data_meta_handler, k, v)

    def set_query_parameters(self, **kwargs):
        if not self._has_data_pattern or not self._query_string_meta_handler:
            return
        for k, v in kwargs.items():
            setattr(self._query_string_meta_handler, k, v)
