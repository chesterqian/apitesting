import re
import json
import pprint
import sys
import os
# sys.path.append(os.path.dirname(__file__))
from base_gen_entity import BaseGenEntity
from base_gen_entity import *


class PostmanEntity(BaseGenEntity):
    def __init__(self, json_content=None, filter_pattern=None):
        super(PostmanEntity, self).__init__(json_content, filter_pattern)

    def _get_all_item(self, item):
        result_list = list()
        self._get_all_item_t(item, result_list)
        return result_list

    def _get_all_item_t(self, item, result_list):
        if not item:
            return
        if isinstance(item, dict):
            if "item" in item and isinstance(item["item"], list):
                for i in item["item"]:
                    self._get_all_item_t(i, result_list)
            else:
                result_list.append(item)
        else:
            print("Unknown item type {}".format(type(item)))
        return result_list

    def pre_process_entity(self, meta_handler):
        # replace path var (:var) to env var ({{var}})
        raw_url = meta_handler.request_url_raw
        raw_url = re.sub(":([a-zA-Z-_]+)", r"{{\1}}", raw_url)
        meta_handler.request_url_raw = raw_url
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
        queries = self._meta_handler.request_url_query
        if queries:
            queries_list = list()
            for i in queries:
                queries_list.append(
                    "{}={}".format(i["key"], i["value"]))
            return "&".join(queries_list)

    def _get_post_data(self):
        _request_body = self._meta_handler.request_body
        if _request_body and "mode" in _request_body:
            mode = _request_body["mode"]
            if mode == "raw":
                return _request_body["raw"]
            elif mode in ["formdata", "urlencoded"]:
                formdata = _request_body[mode]
                t = dict()
                for item in formdata:
                    if item["type"] == "text":
                        t[item["key"]] = item["value"]
                    elif item["type"] == "file":
                        # t[item["key"]] = ""
                        pass
                return json.dumps(t)
            else:
                return None

    def _get_path(self):
        raw_url = self._meta_handler.request_url_raw
        path_search = re.search(REG_PATH_PATTERN, raw_url)
        root_path_search = re.search(REG_PATH_PATTERN_WITH_ROOT_PATH,
                                     raw_url)
        if path_search:
            return path_search.group(1)
        elif root_path_search:
            return root_path_search.group(1)
        else:
            raise Exception('url path parse error, url: {url}'.format(
                url=raw_url))

    def _get_cls_name(self):
        name = self._get_path()
        name = name.title()
        name = re.sub(REG_CLS_NAME_POLISHING_PATTERN, '',
                      name.title()) + 'Entity'
        return name

    def _get_url_pattern(self):
        _url = self._meta_handler.request_url_raw
        _url_pattern = _url
        ind = _url.find("?")
        if ind > -1:
            _url_pattern = _url[:ind + 1]
        _url_pattern = re.sub(REG_DOMAIN_PATTERN, "%s", _url_pattern)
        return _url_pattern

    def _get_value_from_headers(self, key, ignorecase=True):
        """
        header format:
        'request_headers': [{'key': 'Content-Type',
                            'value': 'application/json'}]
        """
        for h in self._meta_handler.request_header:
            if h["key"] == key:
                return h["value"]
            elif ignorecase and h["key"].lower() == key.lower():
                return h["value"]

    def _get_content_type(self):
        if self._meta_handler.request_header:
            content_type = self._get_value_from_headers('Content-Type')
            if content_type:
                content_type = re.search(r'json',
                                    content_type.lower()) and 'json' \
                                or re.search(r'form',
                                    content_type.lower()) and 'form' \
                                or content_type.lower()
                return content_type

        return "json"

    def _get_host(self):
        # return _get_value_from_headers(request_headers, 'Host')
        return re.search(REG_DOMAIN_PATTERN,
                         self._meta_handler.request_url_raw).group()

    def _get_headers(self):
        t = dict()
        for h in self._meta_handler.request_header:
            item = {h["key"]: h["value"]}
            t.update(item)
        return t

    def _get_request_name(self):
        n = self._meta_handler.name
        if isinstance(n, list):
            n = n[0]
        return re.sub(r"\.|/|\\|\s", "_", n) + "_entity"

    def _get_url(self):
        return self._meta_handler.request_url_raw

    def _get_method(self):
        return self._meta_handler.request_method

    def check_form_send_file(self):
        _request_body = self._meta_handler.request_body
        if _request_body and "mode" in _request_body:
            mode = _request_body["mode"]
            if mode in ["formdata", "urlencoded"]:
                formdata = _request_body[mode]
                t = list()
                for item in formdata:
                    if item["type"] == "file":
                        t.append(item["key"])
                return t
            else:
                return None


def test():
    import pprint
    path = 'demo/b.json'
    json_content = None
    with open(path, "r", encoding="UTF-8") as f:
        json_content = json.loads(f.read())
    entity = PostmanEntity(json_content=json_content)
    next_entity = entity.next_entity()
    while True:
        print("HHHHH")
        try:
            module_dict = next(next_entity)
            pprint.pprint(module_dict)
        except StopIteration:
            break


if __name__ == '__main__':
    test()
