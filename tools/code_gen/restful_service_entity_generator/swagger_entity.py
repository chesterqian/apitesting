import re
import json
import pprint
import sys
import os
import copy
# sys.path.append(os.path.dirname(__file__))
from base_gen_entity import BaseGenEntity
from base_gen_entity import *


class SwaggerEntity(BaseGenEntity):
    def __init__(self, json_content=None, filter_pattern=None):
        super(SwaggerEntity, self).__init__(json_content, filter_pattern)
        self.temp_vars = None
        self._host = json_content.get("host")
        self._basePath = json_content.get("basePath")

    def _get_all_item(self, json_content):
        result_list = list()
        for path, value in json_content["paths"].items():
            for method, content in value.items():
                if content.get("deprecated", False) is True:
                    continue
                entity = content
                entity.update({
                    "method": method,
                    "path": path
                })
                result_list.append(entity)
        return result_list

    def pre_process_entity(self, meta_handler):
        # replace path var (:var) to env var ({{var}})
        path = meta_handler.path
        path = re.sub("{([a-zA-Z-_]+)}", r"{{\1}}", path)
        meta_handler.path = path

        self.temp_vars = {
            "headers": dict(),
            "queries": list(),
            "files": list(),
            "body_data": dict()
        }
        if not meta_handler.parameters:
            return
        for item in meta_handler.parameters:
            name = item["name"]
            in_type = item["in"]
            if in_type == "header":
                self.temp_vars["headers"][name] = ""
            elif in_type == "query":
                query_str = "{}={}".format(name, "None")
                self.temp_vars["queries"].append(query_str)
            elif in_type == "body":
                self.temp_vars["body_data"][name] = None
            elif in_type == "formData":
                p_type = item["type"]
                if p_type == "file" or \
                        (p_type == "array" and
                         item["items"]["type"] == "file"):
                    self.temp_vars["files"].append(name)
                else:
                    self.temp_vars["body_data"][name] = None
            elif in_type == "path":
                pass
            else:
                pass
        self.temp_vars["queries"] = "&".join(self.temp_vars["queries"])

    def filter(self, patten):
        index = 0
        for i in self._meta_handler.request_url:
            if not re.search(patten, i):
                self._entity_list.pop(index)
                index -= 1
            index += 1
        return self._entity_list

    def _get_query_string(self):
        return self.temp_vars.get("queries", None)

    def _get_post_data(self):
        return self.temp_vars.get("body_data", None)

    def _get_path(self):
        if self._basePath == "/":
            return self._meta_handler.path
        else:
            return self._basePath + self._meta_handler.path

    def _get_cls_name(self):
        name = self._meta_handler.path
        name = name.title()
        name = re.sub(REG_CLS_NAME_POLISHING_PATTERN, '',
                      name.title()) + 'Entity'
        return name

    def _get_url_pattern(self):
        url_pattern = "%s{}".format(self._get_path())
        query_str = self._get_query_string()
        if query_str:
            url_pattern = url_pattern + "?"
        return url_pattern

    def _get_value_from_headers(self, key, ignorecase=True):
        return self.temp_vars["headers"][key]

    def _get_content_type(self):
        content_type = self._meta_handler.consumes
        if content_type:
            content_type = content_type[0]
            content_type = re.search(r'json',
                                     content_type.lower()) and 'json' \
                           or re.search(r'form',
                                        content_type.lower()) and 'form' \
                           or content_type.lower()
            return content_type

        return "json"

    def _get_host(self):
        return self._host

    def _get_headers(self):
        return self.temp_vars["headers"]

    def _get_request_name(self):
        n = self._meta_handler.operationId
        if isinstance(n, list):
            n = n[0]
        return re.sub(r"\.|/|\\|\s", "_", n) + "_entity"

    def _get_method(self):
        return self._meta_handler.method

    def check_form_send_file(self):
        return self.temp_vars["files"]


def test():
    import pprint
    path = 'demo/swagger2.json'
    json_content = None
    with open(path, "r", encoding="UTF-8") as f:
        json_content = json.loads(f.read())
    entity = SwaggerEntity(json_content=json_content)
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
