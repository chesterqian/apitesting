import re
import json
import pprint
import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_gen_entity import BaseGenEntity
from base_gen_entity import *


class HarEntity(BaseGenEntity):
    def __init__(self, json_content=None, filter_pattern=None):
        super(HarEntity, self).__init__(json_content, filter_pattern)

    def _get_all_item(self, item):
        if not item:
            return
        result_list = item['log']['entries']
        return result_list

    def filter(self, patten):
        index = 0
        for i in self._meta_handler.request_url:
            if not re.search(patten, i):
                self._json_content.pop(index)
                index -= 1
            index += 1

        return self._json_content

    def _get_query_string(self):
        if self._meta_handler.queryString:
            def _get():
                query_items = self._meta_handler.queryString
                iter_query_items = iter(query_items)
                out_string = ''
                while True:
                    in_string = yield out_string
                    item = next(iter_query_items)
                    values = list(item.values())
                    out_string = '%s=%s' % (values[0], values[1])
                    if in_string:
                        in_string += '&'
                    out_string = in_string + out_string

            generator = _get()
            query_string = next(generator)
            while True:
                try:
                    query_string = generator.send(query_string)
                except StopIteration:
                    break
            return query_string

    def _get_post_data(self):
        postData = self._meta_handler.postData
        if not postData:
            return None
        if postData.get("text", None):
            return postData["text"]
        if postData.get("params", None):
            params_names = postData["params"]["name"]
            params_values = postData["params"]["value"]
            if not isinstance(params_names, list):
                params_names = [params_names]
            if not isinstance(params_values, list):
                params_values = [params_values]
            if len(params_names) == len(params_values):
                return dict(list(zip(params_names, params_values)))

    def _get_path(self):
        url = self._meta_handler.request_url
        path_search = re.search(REG_PATH_PATTERN, url)
        if path_search:
            return path_search.group(1)
        else:
            raise Exception(
                'url path parse error, url: {url}'.format(url=url))

    def _get_cls_name(self):
        name = self._get_path()
        name = name.title()
        name = re.sub(REG_CLS_NAME_POLISHING_PATTERN, '',
                      name.title()) + 'Entity'
        return name

    def _get_url_pattern(self):
        url = self._meta_handler.request_url
        url_pattern = url
        ind = url.find("?")
        if ind > -1:
            url_pattern = url[:ind + 1]
        url_pattern = re.sub(REG_DOMAIN_PATTERN, "%s", url_pattern)
        return url_pattern

    def _get_value_from_headers(self, key, ignorecase=True):
        """
        header format:
        'request_headers': [{'name': 'Content-Type',
                            'value': 'application/json'}]
        """
        request_header = self._meta_handler.request_header
        if not request_header:
            return None
        for h in request_header:
            if h["name"] == key:
                return h["value"]
            elif ignorecase and h["name"].lower() == key.lower():
                return h["value"]

    def _get_content_type(self):
        request_headers = self._meta_handler.request_headers
        if request_headers:
            content_type = self._get_value_from_headers('Content-Type') \
                           or self._get_value_from_headers('content-type')
            if content_type:
                content_type = re.search(r'json',
                                         content_type.lower()) and 'json' \
                               or re.search(r'form',
                                            content_type.lower()) and 'form'

                return content_type
            else:
                return "json"

    def _get_host(self):
        # return _get_value_from_headers(request_headers, 'Host')
        url = self._meta_handler.url
        return re.search(REG_DOMAIN_PATTERN, url).group()

    def _get_url(self):
        return self._meta_handler.url

    def _get_headers(self):
        t = dict()
        for h in self._meta_handler.request_headers:
            item = {h["name"]: h["value"]}
            t.update(item)
        return t

    def _get_method(self):
        return self._meta_handler.request_method


def test():
    import pprint
    path = 'demo/har.json'
    json_content = None
    with open(path) as f:
        json_content = json.loads(f.read())
    entity = HarEntity(json_content=json_content)
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

    # from code_gen_service_entity import CodeGenServiceEntity
    #
    # code_gen_entity = CodeGenServiceEntity(domain_name='10.199.101.211:8080', data=json_content)
    # code_gen_entity.send_request()
    # print code_gen_entity.data
