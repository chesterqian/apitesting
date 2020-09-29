import re
import json
import pprint
import sys
import os
sys.path.append(os.path.dirname(__file__))
from autotest import BaseMetaDataHandlerV2 as MetaHandler

REG_DOMAIN_PATTERN = r'^(((http://)|(https://))?[a-zA-Z0-9\-_\.\{\}]+(:(\d+)|(\{\{.+\}\}))?)'
REG_PATH_PATTERN = r'[a-zA-Z0-9\}](/[a-zA-Z0-9/\-_\{\}]*\??)'
REG_PATH_PATTERN_WITH_ROOT_PATH = r'[a-zA-Z0-9\}](/?\?).*'
REG_CLS_NAME_POLISHING_PATTERN = r'[.:\?/{}-]'
REG_URL_PATTERN = r'(.+\?)'


class BaseGenEntity:
    def __init__(self, json_content=None, filter_pattern=None):
        super(BaseGenEntity, self).__init__()

        self._meta_handler = None
        self._filter_pattern = filter_pattern

        if json_content:
            try:
                item_list = self._get_all_item(json_content)
                if not isinstance(item_list, list):
                    item_list = [item_list]
                self._entity_list = item_list
            except (TypeError, KeyError):
                self._entity_list = json_content

            if self._filter_pattern:
                self.filter(self._filter_pattern)

    def _get_all_item(self, item):
        '''
        parse json format and get entity list and return result_list
        :param item:
        :return: item
        '''
        return item

    def pre_process_entity(self, meta_handler):
        return None

    def filter(self, patten):
        index = 0
        for i in self._meta_handler.request_url:
            if not re.search(patten, i):
                self._entity_list.pop(index)
                index -= 1
            index += 1
        return self._entity_list

    def _get_query_string(self):
        return ""

    def _get_post_data(self):
        return ''

    def _get_path(self):
        return ""

    def _get_cls_name(self):
        return ""

    def _get_url_pattern(self):
        return ""

    def _get_value_from_headers(self, key, ignorecase=True):
        """
        header format:
        'request_headers': [{'name': 'Content-Type',
                            'value': 'application/json'}]
        """
        for h in self._meta_handler.request_header:
            if h["name"] == key:
                return h["value"]
            elif ignorecase and h["name"].lower() == key.lower():
                return h["value"]

    def _get_content_type(self):
        return "json"

    def _get_host(self):
        return ""

    def _get_headers(self):
        return None

    def _get_request_name(self):
        return ""

    def _get_url(self):
        return ""

    def _get_method(self):
        return ""

    def check_form_send_file(self):
        return None

    def next_entity(self):
        temp_entity_list = self._entity_list
        while temp_entity_list:
            entity_json_content = temp_entity_list.pop(0)
            self._meta_handler = MetaHandler(entity_json_content)
            self.pre_process_entity(self._meta_handler)

            request_name = self._get_request_name()
            method_type = self._get_method()
            request_headers = self._get_headers()
            post_data = self._get_post_data()
            query_data = self._get_query_string()
            host = self._get_host()
            cls_name = self._get_cls_name()
            content_type = self._get_content_type()
            url_path = self._get_path()
            url_pattern = self._get_url_pattern()
            has_data_pattern = True

            entity_attr_map = {
                "request_name": request_name,
                'method_type': method_type.lower(),
                'cls_name': str(method_type.title() + cls_name),
                'url_pattern': url_pattern,
                'path': url_path,
                'request_headers': request_headers,
                'body_data': post_data,
                'query_data': query_data,
                'content_type': content_type,
                'has_data_pattern': has_data_pattern,
                'host': host
            }

            files = self.check_form_send_file()
            if files:
                entity_attr_map.update({
                    "method_type": "multipart_post",
                    "send_files": files
                })
            entity_name = method_type.title() + cls_name
            yield {entity_name: entity_attr_map}


def test():
    import pprint
    json_content = {"a": 1}
    entity = BaseGenEntity(json_content=json_content)
    next_entity = entity.next_entity()
    while True:
        try:
            module_dict = next(next_entity)
            print("HHHHH")
            pprint.pprint(module_dict)
        except StopIteration:
            break


if __name__ == '__main__':
    test()
