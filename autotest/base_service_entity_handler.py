# -*- coding:utf-8 -*-
import copy
import inspect
import json
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import re
from .lib.service_helper import ServiceHelper
from .lib.json_handler import handle_item_in_json, set_field_value
from .meta_data_handler import BaseMetaDataHandler
from .utility import Utility
from .exception import BadStatusCodeException


def retrieve_value_from_dict(target_key, target_dict):
    """
    retrieve value from dict whose keys may be tuple and input target_key is in the tuple.
    """
    for key in list(target_dict.keys()):

        if isinstance(key, tuple):
            if target_key in key:
                return target_dict[key]
        elif target_key == key:
            return target_dict[target_key]


def set_request_data_from_args(func):
    def wrapper(entity, *args, **kwargs):
        if not entity._data and entity._has_data_pattern:
            entity._save_send_request_kwargs(kwargs)
            function_inspect = inspect.getfullargspec(entity._set_data_pattern)

            if len(function_inspect.args) <= 1 and \
                    function_inspect.varargs is None and function_inspect.keywords is None:
                entity._set_data_pattern()
            else:
                args, kwargs = entity._set_data_pattern(*args,
                                                        **kwargs) or (
                                   args, kwargs)

            data_pattern = entity.current_data_pattern
            
            if data_pattern:
                data = ''

                def handle_str_fake(data):
                    find_fake_phrases_pattern = r'fake(?:_en|_cn)?.\w*'
                    find_only_fake_pattern = r'^fake(?:_en|_cn)?.'
                    if re.search(find_fake_phrases_pattern, data):
                        phrases = re.findall(find_fake_phrases_pattern,
                                             data)
                        for fake_item in phrases:
                            fake_object = getattr(entity.utility,
                                                  re.search(
                                                      r"^fake(?:_en|_cn)?",
                                                      fake_item).group())

                            fake_attribute = re.sub(find_only_fake_pattern,
                                                    '',
                                                    fake_item)
                            faked_value = getattr(fake_object,
                                                  fake_attribute)()
                            data = re.sub(find_fake_phrases_pattern,
                                          faked_value, data, 1)
                    return data

                def handle_str_data_patten():
                    def prepare_url_dict(l_arg):
                        rt_dict = {}
                        keys = [t_items[0] for t_items in l_arg]
                        values = [str(t_items[1]).encode('utf-8') for
                                  t_items in l_arg]
                        for item in keys:
                            index_num = keys.index(item)
                            temp_count = keys.count(item)
                            if temp_count > 1:
                                temp_l = tuple(
                                    [i for i in
                                     values[
                                     index_num:index_num + temp_count]])
                                rt_dict.update({item: temp_l})
                            else:
                                rt_dict.update({item: values[index_num]})
                        return rt_dict

                    if args:
                        parsed_data_pattern = urllib.parse.parse_qsl(
                            data_pattern)
                        number_of_args_difference = len(
                            parsed_data_pattern) - len(args)
                        zipped_list = list(zip([list(i)
                                                for i in parsed_data_pattern],
                                               args))
                        tmp_list = [list(i) for i in zipped_list]
                        new_list = []
                        for i in tmp_list:
                            i[0][1] = i[1]
                            new_list.append(i[0])
                        data = urllib.parse.urlencode(prepare_url_dict(new_list), 1)
                        if number_of_args_difference:
                            data += '&' + \
                                    urllib.parse.urlencode(prepare_url_dict(
                                        parsed_data_pattern[
                                        -number_of_args_difference:]), 1)
                    else:
                        data = data_pattern

                    if kwargs:
                        decode_str = lambda x: (type(x) == bytes) and x.decode() or str(x)
                        keyword_sub_pattern = "=[\u4e00-\u9fa5/%A-Za-z0-9_.-]*(?=&)?"
                        for k in kwargs:
                            if not re.search(k + keyword_sub_pattern, data):
                                raise KeyError('kwargs does not exists!')
                            data = decode_str(
                                re.sub(k + keyword_sub_pattern,
                                       k + '=' + decode_str(kwargs[k]),
                                       decode_str(data)))

                    return data

                def handle_dict_data_pattern():
                    if kwargs:
                        for k in kwargs:
                            value = copy.copy((kwargs[k]))
                            if value is None:
                                node, key = entity.get_json_value_by_node_key(k)
                                handle_item_in_json(data_pattern, node, key, mode='pop_key')
                            else:
                                set_field_value(data_pattern, k, value)
                    if args:
                        raise Exception('*args is not supported now!')

                    data = data_pattern

                    return data

                def transform_data_pattern_to_json(temp_data_pattern):
                    try:
                        temp_data_pattern = json.loads(temp_data_pattern)
                    except ValueError:
                        return False
                    return temp_data_pattern

                if isinstance(data_pattern, str):
                    data_pattern = handle_str_fake(data_pattern)
                    tmp_data_pattern = transform_data_pattern_to_json(
                        data_pattern)
                    if tmp_data_pattern:
                        data_pattern = tmp_data_pattern
                        data = handle_dict_data_pattern()
                    else:
                        data = handle_str_data_patten()
                elif isinstance(data_pattern, dict):
                    data_pattern = handle_str_fake(json.dumps(data_pattern))
                    data_pattern = json.loads(data_pattern)
                    data = handle_dict_data_pattern()

                entity._data = data
            else:
                raise ValueError(
                    '_current_data_pattern is not properly set')

        entity._handle_data_before_request()

        if entity.delete_fields:
            entity._delete_fields_as_required()

        return func(entity, *args, **kwargs)

    return wrapper


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


class BaseServiceEntityHandler(object, metaclass=EntityMetaClass):
    def __init__(self, url_string=None, data='', has_data_pattern=True,
                 files=None, method_type='get',
                 request_content_type='form', domain_name=None,
                 cookies=None,
                 token=None, stream=False, request_headers=None,
                 request_timeout=None):
        self._url_string = url_string
        self._data = data
        self._has_data_pattern = has_data_pattern
        self._current_data_pattern = None
        self._request_content_type = request_content_type
        self._domain_name = domain_name
        self._method_type = method_type
        self._files = files
        self._default_url_pattern = url_string
        self._default_data = data
        self._default_request_content_type = request_content_type
        self._default_method_type = method_type
        self._json_content = None
        self._response = None
        self.cookies = cookies
        self._token_in_header = token
        self.stream = False
        self._request_headers = request_headers
        self._request_timeout = request_timeout
        self._special_node_attributes = []
        self._special_key_attributes = []
        # 将类变量赋给实例变量
        self.service_helper = self._service_helper

        self.delete_fields = list()
        self._send_request_kwargs = None
        self._response_meta_data = None

    @property
    def json_content(self):
        return self._json_content

    @property
    def response_content(self):
        if not self._response:
            self._request()

        return self._response

    @property
    def current_data_pattern(self):
        return self._current_data_pattern

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
            if self._method_type == 'post':
                self._response = self.service_helper.call_service_with_post(
                    self._url_string, self._data,
                    content_type=self._request_content_type,
                    domain_name=self._domain_name, cookies=self.cookies,
                    token=self._token_in_header, request_headers=self._request_headers,
                    request_timeout=self._request_timeout)
            elif self._method_type == 'get':
                self._response = self.service_helper.call_service_with_get(
                    self._url_string, self._data,
                    domain_name=self._domain_name, cookies=self.cookies,
                    token=self._token_in_header, stream=self.stream,
                    request_headers=self._request_headers,
                    request_timeout=self._request_timeout)
            elif self._method_type == 'put':
                self._response = self.service_helper.call_service_with_put(
                    self._url_string, self._data,
                    content_type=self._request_content_type,
                    domain_name=self._domain_name, cookies=self.cookies,
                    token=self._token_in_header, request_headers=self._request_headers,
                    request_timeout=self._request_timeout)
            elif self._method_type == 'multipart_post':
                self._response = self.service_helper.call_service_with_multipart_post(
                    self._url_string, self._data,
                    self._files, domain_name=self._domain_name,
                    cookies=self.cookies, token=self._token_in_header,
                    request_headers=self._request_headers,
                    request_timeout=self._request_timeout)
            elif self._method_type == 'delete':
                self._response = self.service_helper.call_service_with_delete(
                    self._url_string, self._data,
                    domain_name=self._domain_name, cookies=self.cookies,
                    token=self._token_in_header, request_headers=self._request_headers,
                    request_timeout=self._request_timeout)
        except BadStatusCodeException as e:
            self._response = e.response
            self._handle_response()

            raise e

        if self._response:
            self._handle_response()

    def _handle_response(self):
        try:
            self._json_content = self._response.json()
        except ValueError:
            self._json_content = self._transform_response_body_to_dict(self._response.content)
        self._response_meta_data = BaseMetaDataHandler(self._json_content)

        self.cookies = self._response.cookies

    def update_response_json(self, json_content):
        self._json_content = json_content
        self._response_meta_data = BaseMetaDataHandler(self._json_content)

    def _reload(self):
        self._url_string, self._data, self._method_type = \
            self._default_url_pattern, self._default_data, self._default_method_type

        self._request()

    def _save_send_request_kwargs(self, kwargs):
        self._send_request_kwargs = kwargs

    def set_delete_fields(self, delete_list):
        self.delete_fields = delete_list

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

        for field in self.delete_fields:
            split_field = field.split(".")
            delete_in_dict(self._data, split_field)

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

    def _transform_response_body_to_dict(self, response_body):
        '''
        The method can help solve parsing non-json response body. If need, entity class should customize this function.
        :parameter: the response_body , type str
        :return:  the dict transformed from your own response body
        '''
        return None

    def set_request_data(self, data):
        self._has_data_pattern = False
        self._data = data

    def get_request_data(self):
        return self._data

    def _set_data_pattern(self, *args, **kwargs):
        raise NotImplementedError(
            "Please override '_set_data_pattern' to set _current_data_pattern for request data")

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
        self._data = self._default_data + partial_query_data
        self._request()

        return self

    @set_request_data_from_args
    def send_request(self, *args, **kwargs):
        self._request()

    def get_json_value_by_node_key(self, attribute):
        if attribute in self._special_node_attributes:
            node, key = attribute, None
        elif attribute in self._special_key_attributes:
            raw_list = attribute.split('_')
            node, key = raw_list[0], '_' + raw_list[1]
        else:
            raw_list = attribute.split('_')
            if len(raw_list) == 1:
                node, key = attribute, None
            elif len(raw_list) == 2:
                node, key = raw_list[0], raw_list[1]
            else:
                raise Exception(
                    '''The attribute, named: %s, don't suitable for getting in this way.''' % attribute)
        return node, key
