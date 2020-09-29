# -*- coding: utf-8 -*-
import os
import re
import json
import astor
import getopt
import sys
from pprint import pprint
from copy import deepcopy
sys.path.append(os.path.dirname(__file__))
from ast_operator import *

from har_entity import HarEntity
from postman_entity import PostmanEntity
from swagger_entity import SwaggerEntity

default_dst_dir = "./temp_entities_dir"

Usage = '''\
Usage:
    entity-generator -t <src_type> -s <source_har_file_path> -d <target_dir>
General:
    Generate autotest service entities by har file
    -s path\t Required, source har file path 
    -u web swagger url\t Required for web swagger
    -d folder\t target generated entities dir, default: {}
    -t src_type\t Source type, one of [har, postman, swagger], default: postman
Note:
    postman json should be postman v2.1
    swagger json should be swagger v2.0
Example:  
    entity-generator -t postman -s postman.json -d ./entities
'''.format(default_dst_dir)

ENTITY_TEMPLATE_NAME = "entity_template_v2.py"
CURRENT_PATH = os.path.dirname(__file__)
CURRENT_PATH = CURRENT_PATH if CURRENT_PATH.strip() else '.'
COMPLETE_FILE_NAME = os.path.join(CURRENT_PATH, "templates",
                                  ENTITY_TEMPLATE_NAME)


def _to_lower(matched):
    if matched.group('first'):
        return matched.group().lower()
    return '_' + matched.group().lower()


def _format_query_data(query_data):
    data = ''
    for i in query_data:
        if i == query_data[0]:
            data += str(i) + '=%s'
        else:
            data += '&' + str(i) + '=%s'
    return data


def create_py_modules(entity_instance, dst_dir, mode='file'):
    # mode: 'file'/'json'
    # 生成或切换目录
    if not dst_dir:
        raise Exception("No dst dir specified")

    module_entity = entity_instance
    node = load_ast_from_py_file(COMPLETE_FILE_NAME)
    next_entity = module_entity.next_entity()
    json_template = {}
    entity_count = 0

    while True:
        try:
            module_dict = next(next_entity)

            for module_item in list(module_dict.values()):
                _node = deepcopy(node)
                handle_cls_name(_node.body, 'Foo', module_item['cls_name'])
                handel_cls_in_main(_node.body, 'Foo',
                                   module_item['cls_name'])

                # make entity init args according to {{var}} in path
                module_item['url_pattern'] = handle_path_parameters_with_pattern(
                    _node.body,
                    module_item['url_pattern'],
                    r"\{\{([a-zA-Z_\-]+)\}\}")

                # make files init args according to file form body
                send_files = module_item.get("send_files", None)
                if send_files and len(send_files) > 0:
                    handle_send_files_form(_node.body, module_item["send_files"])
                # set global assignment
                # set value for PATH
                handle_global_assignment(_node.body, 'PATH', module_item['path'])
                # set value for METHOD_TYPE
                handle_global_assignment(_node.body, 'METHOD_TYPE',
                                         module_item['method_type'])

                content_type = module_item['content_type']
                if content_type:
                    content_type = str(re.search(r'json|form', content_type).group())
                    # set value for CONTENT_TYPE
                    handle_global_assignment(_node.body, 'CONTENT_TYPE',
                                             content_type)
                # set value for domain_name
                handle_global_assignment(_node.body, 'DOMAIN_NAME',
                                         module_item['host'])
                # set value for url
                handle_global_assignment(_node.body, 'URL',
                                         module_item['url_pattern'])
                # set value for request_headers
                handle_global_assignment(_node.body, 'REQUEST_HEADERS',
                                         module_item['request_headers'])
                # set value for HAS_DATA_PATTERN
                handle_global_assignment(_node.body, 'HAS_DATA_PATTERN',
                                         module_item['has_data_pattern'])
                # set request data
                # set value for BODY_DATA
                handle_global_assignment(_node.body, 'BODY_DATA',
                                         module_item['body_data'])

                # set value for QUERY_DATA
                handle_global_assignment(_node.body, 'QUERY_DATA',
                                         module_item['query_data'])
                # Written to the .py file
                if "request_name" in module_item and module_item["request_name"]:
                    base_name = module_item["request_name"]
                else:
                    base_name = module_item["cls_name"]
                # file_name = re.sub(r'(?P<first>^[A-Z])|[A-Z]', _to_lower,
                #                    base_name) + '.py'
                file_name = re.sub(r"\.|/|\\|\s", "_", base_name) + '.py'

                # prepare code lines to inject
                temp_lines = astor.to_source(_node)
                lines = re.sub(r"\\n[ ]+'", '\n    """',
                               re.sub(r"'\\n", '"""\n', temp_lines))
                lines = re.sub(r"\\n([ ]*)", lambda m: '\n' + m.group(1), lines)

                if mode == 'file':
                    filepath = dst_dir + os.sep + file_name
                    with open(filepath, 'w') as py_module:
                        py_module.write(lines)
                    print("Entity %s \tsaved into %s" %
                          (module_item['cls_name'], file_name))

                if mode == 'json':
                    json_template.update({module_item['cls_name']: lines})

                entity_count += 1

        except StopIteration:
            print("\n{} entities created".format(entity_count))
            if json_template:
                return json_template
            break


def main():
    opts, args = getopt.getopt(sys.argv[1:], 'hs:d:t:u:',
          [  
            'src-har=',   
            'dst-dir=',
            'src-url=',
            'type=',
            'help'  
            ]  
          )
    src_file = None
    dst_dir = default_dst_dir
    # src_url only for swagger web
    src_url = None
    src_type = "postman"

    for option, value in opts:  
        if  option in ["-h", "--help"]:
            print(Usage)
            sys.exit(1)
        elif option in ['--src-file', '-s']:  
            src_file = value
        elif option in ['--src-url', '-u']:
            src_url = value
        elif option in ['--dst-dir', '-d']:  
            dst_dir = value  
        elif option in ['--type', '-t']:  
            src_type = value  
        else:
            print(Usage)
            print("Unknown option {}".format(option))
            sys.exit(1)
    if not src_file and not src_url:
        print(Usage)
        print("Error: -s or -u is required")
        sys.exit(1)

    dst_dir = os.path.abspath(dst_dir)
    print("Target Dir: {}\n".format(dst_dir))
    if not os.path.isdir(dst_dir):
        os.mkdir(dst_dir)
        os.path.join(dst_dir)

    entity_map = {
        "postman": PostmanEntity,
        "har": HarEntity,
        "swagger": SwaggerEntity
    }
    filter_pattern = ""
    json_data = None
    entity_class = entity_map.get(src_type, None)
    if not entity_class:
        print(Usage)
        print("Error: Wrong Type")
        sys.exit(1)
    if src_file:
        with open(src_file, 'r', encoding='UTF-8') as f:
            json_data = json.loads(f.read())
    elif src_url:
        from swagger_dump import dump_swagger_from_url, save_swagger_json_to_file
        json_data = dump_swagger_from_url(src_url)
        save_swagger_json_to_file(json_data, "current_swagger.json")
        print("Swagger api doc has been saved to current_swagger.json\n")
    entity = entity_class(json_data, filter_pattern)
    r = create_py_modules(entity, dst_dir, 'file')


if __name__ == '__main__':
    main()

