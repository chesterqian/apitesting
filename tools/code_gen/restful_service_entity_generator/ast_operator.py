# -*- coding: utf-8 -*-
import os
import re
import json
import sys
from _ast import *
import astor
from copy import deepcopy
sys.path.append(os.path.dirname(__file__))

ARG_VALUE_TYPE_MAP_ATTR = {
    int: 'n',
    float: 'n',
    list: 's',
    tuple: 's',
    str: 's',
    bool: 'id',
    dict: 's'
}


def load_ast_from_py_file(filename):
    node = astor.parsefile(filename)
    return node


def _handle_class_doc(node_body, response_dict):
    """
    Add comments for entity class
    """
    for sub_node in node_body:
        if sub_node.__class__.__name__ == 'ClassDef':
            for i in sub_node.body:
                if i.__class__.__name__ == 'Expr':
                    i.value.s = i.value.s % json.dumps(response_dict, indent=2)


def build_ast_data(data):
    if isinstance(data, dict):
        keys = list()
        values = list()
        for k, v in data.items():
            keys.append(build_ast_data(k))
            values.append(build_ast_data(v))
        d = Dict(keys=keys, values=values)
        return d
    elif isinstance(data, list):
        elts = list()
        for i in data:
            item = build_ast_data(i)
            elts.append(item)
        l = List(elts=elts)
        return l
    elif isinstance(data, set):
        elts = list()
        for i in data:
            item = build_ast_data(i)
            elts.append(item)
        s = Set(elts=elts)
        return s
    elif isinstance(data, tuple):
        elts = list()
        for i in data:
            item = build_ast_data(i)
            elts.append(item)
        t = Tuple(elts=elts)
        return t
    elif isinstance(data, int) or isinstance(data, float):
        return Num(n=data)
    elif isinstance(data, bool):
        return NameConstant(value=data)
    elif isinstance(data, str):
        return Str(s=data)
    elif isinstance(data, bytes):
        return Bytes(s=data)
    elif data is None:
        return NameConstant(value=None)
    else:
        raise Exception("Unknown type: {}".format(type(data)))


def handle_global_assignment(node_body, arg_name, arg_value):
    """
    assign value for global var name, note arg_name must exist
    dict and list will json.dump
    """
    # dict type arg is not supported now
    if arg_value:
        for sub_node in node_body:
            if sub_node.__class__.__name__ == 'Assign':
                target = sub_node.targets[0]
                value = sub_node.value

                if target.id == arg_name:
                    # attr = ARG_VALUE_TYPE_MAP_ATTR[type(arg_value)]
                    #
                    # if type(arg_value) == dict:
                    #     arg_value = json.dumps(arg_value, indent=2)
                    #
                    # setattr(value, attr, arg_value)
                    sub_node.value = build_ast_data(arg_value)


def handle_cls_name(node_body, old_name, new_name):
    """
    rename entity class name
    """
    for sub_node in node_body:
        if sub_node.__class__.__name__ == 'ClassDef':
            if sub_node.name == old_name:
                sub_node.name = new_name
                handle_super_call_in_init(sub_node.body, old_name, new_name)
                # print astor.dump(node_body)


def handle_path_parameters_swagger(node_body, init_args):
    for sub_node in node_body:
        if sub_node.__class__.__name__ == 'ClassDef':
            for i in sub_node.body:
                if i.__class__.__name__ == 'FunctionDef' and i.name == '__init__':
                    for item in init_args:
                        temp_args = deepcopy(i.args.args[-1])
                        temp_args.id = re.sub(r'(?P<first>^[A-Z])|[A-Z]',
                                              _to_lower, item)
                        temp_args.col_offset = temp_args.col_offset + len(
                            item) + 2
                        i.args.args.append(temp_args)


def handle_path_parameters_with_pattern(node_body, path,
                                        pattern=r"\{\{([a-zA-Z_\-]+)\}\}"):
    init_vars = re.findall(pattern, path)
    if not init_vars:
        return path

    return_path = re.sub(pattern, "{}", path)

    for sub_node in node_body:
        if sub_node.__class__.__name__ == 'ClassDef':
            for i in sub_node.body:
                if i.__class__.__name__ == 'FunctionDef' and i.name == '__init__':
                    for item in init_vars:
                        temp_args = deepcopy(i.args.args[-1])
                        temp_args.arg = item
                        i.args.args.append(temp_args)
                    for _expr in i.body:
                        expr_value = _expr.value
                        if isinstance(expr_value, Call) and expr_value.func.attr == '__init__':
                            for kw in expr_value.keywords:
                                if kw.arg == 'url_string':
                                    url_args = list()
                                    for item in init_vars:
                                        url_args.append(Name(id=item))
                                    value = Call(
                                        func=Attribute(value=Name(id='URL'),
                                                       attr='format'),
                                        args=url_args,
                                        keywords=[])
                                    kw.value = value
    return return_path


def handle_send_files_form(node_body, send_files):
    for sub_node in node_body:
        if sub_node.__class__.__name__ == 'ClassDef':
            for i in sub_node.body:
                if i.__class__.__name__ == 'FunctionDef' and i.name == '__init__':
                    for fd in send_files:
                        temp_args = deepcopy(i.args.args[-1])
                        temp_args.arg = fd
                        i.args.args.append(temp_args)
                    assign_keys = list()
                    assign_values = list()
                    for fn in send_files:
                        assign_keys.append(Str(s=fn))
                        assign_values.append((Name(id=fn)))
                    assign_obj = Assign(targets=[Name(id='files')],
                                        value=Dict(keys=assign_keys,
                                                   values=assign_values))
                    i.body.insert(0, assign_obj)
                    for _expr in i.body:
                        expr_value = _expr.value
                        if isinstance(expr_value,
                                      Call) and expr_value.func.attr == '__init__':
                            keywords = expr_value.keywords
                            keywords.insert(len(keywords)-1,
                                            keyword(arg='files',
                                                    value=Name(id='files')))


def handle_super_call_in_init(node_body, old_cls_name, new_cls_name):
    """
    update super class name in __init__
    """
    for i in node_body:
        if i.__class__.__name__ == 'FunctionDef' and i.name == '__init__':
            for expr in i.body:
                if hasattr(expr.value, 'func'):
                    call_as_attribute = expr.value
                    call_as_attribute_args = expr.value.args
                    call_as_attribute_keywords = expr.value.keywords
                    attribute = call_as_attribute.func
                    attr = attribute.attr
                    attr_value = attribute.value

                    if attr_value.__class__.__name__ == 'Call':
                        attr_value_args = attr_value.args
                        attr_value_keywords = attr_value.keywords
                        attr_value_func_name = attr_value.func.id

                        [setattr(i, 'id', new_cls_name)
                         for i in attr_value_args if i.id == old_cls_name]


def handel_cls_in_main(node_body, old_cls_name, new_cls_name):
    """
    rename entity class name in main
    """
    for i in node_body:
        if i.__class__.__name__=='If' and i.test.__class__.__name__=='Compare':
            if not (i.test.left.id=='__name__' and i.test.comparators[0].s=='__main__'):
                continue
            for j in i.body:
                if j.__class__.__name__=='Assign':
                    if j.value.__class__.__name__=='Call' and j.value.func.id==old_cls_name:
                        j.value.func.id = new_cls_name


def main():
    d = {
        "1": 1,
        "2": {
            b"aaa": [0,1,2,3]
        }
    }
    node = build_ast_data(d)
    print(node)
    print(astor.dump(node))


if __name__ == '__main__':
    main()

