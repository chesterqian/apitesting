# -*- coding:utf-8 -*-
import json

def getCleanJsonView(data):
    return json.dumps(data, indent=2)


def getJsonData(data):
    json_data = json.loads(data.read())
    return json_data


def get_stop_polling_flag(mode, values):
    return (mode == 'set' and not values) and True or False


def try_json_loads(data):
    try:
        return json.loads(data)
    except ValueError:
        return False


def handle_item_in_json(candidate, node,
                        key=None, container=None,
                        values=[], mode='get', deep_search=False, **kwargs):
    # value for mode:get,set,pop_key,replace_key_with_value
    # deep_search is False for same keys on the same level
    # deep_search is True for same keys on all level(same&different)

    is_list = kwargs["is_list"] if kwargs.__contains__("is_list") else isinstance(values, list)

    def handle_get_data(data, _key=None):
        if _key:
            if _key in data:
                data = data[_key]
            else:
                return
        container.append(data)

    def handle_set_data(data, _key):
        if _key in data:
            value = values.pop(0) if not is_list else values
            data[_key] = value
        else:
            pass

    def handle_pop_key(data, _key):
        if _key in data:
            data.pop(_key)

    def handle_replace_key_with_value(data, _key):
        if _key in data:
            value = data.pop(_key)

            if values:
                value = values.pop(0)

            if isinstance(value, dict):
                # only supportted when data[_key] is type of dict
                data.update(value)
            else:
                raise Exception('only support dict value')

    def handle(source):
        source_value = source[node]

        if key:

            def _handle_source_value():
                if isinstance(source_value, list):
                    for i in source_value:
                        handle_function(i, key)
                elif isinstance(source_value, dict):
                    handle_function(source_value, key)

            try:
                if isinstance(source_value, list) or isinstance(source_value, dict):
                    _handle_source_value()
                else:
                    # for the sake of capatibilty with form data
                    source_value = try_json_loads(source_value)
                    if source_value:
                        _handle_source_value()
                        source[node] = json.JSONEncoder().encode((source_value))
            except KeyError:
                pass
        else:
            args = ((values,) and (source, node)) or (source_value,)
            handle_function(*args)

    mode_map_function = {
        'get': handle_get_data,
        'set': handle_set_data,
        'pop_key': handle_pop_key,
        'replace_key_with_value': handle_replace_key_with_value
    }

    if container and values:
        msg = 'container and values are mutual exclusive,one of those should be None!'
        raise TypeError(msg)

    if not isinstance(values, list):
        values = [values]

    handle_function = mode_map_function[mode]

    if isinstance(candidate, dict):
        def looping():
            for k in candidate:
                if get_stop_polling_flag(mode, values):
                    break

                handle_item_in_json(candidate[k], node,
                                    key, container, values, mode, deep_search, is_list=is_list)

        if node in candidate:
            handle(candidate)

            if deep_search:
                looping()
        else:
            looping()
    elif isinstance(candidate, list):
        for i in candidate:
            if get_stop_polling_flag(mode, values):
                break
            if not key:
                try:
                    handle(i)
                except (KeyError, TypeError):
                    pass
                continue

            handle_item_in_json(i, node,
                                key, container, values, mode, deep_search, is_list=is_list)


def get_complete_path(json_data, path, base_path=""):
    """
   （because the given path_str may be abbreviated）
    according to the given path， get the complete path string
    :param json_data:
    :param path: a string is used to specify a field in json
    :param base_path: current path
    :return:
    """

    def is_match(match_path):
        return match_path.endswith(path)

    ret_path = None
    if isinstance(json_data, dict):
        for key, value in json_data.items():

            cur_path = ("%s_%s" % (base_path, key)).strip("_").strip(" ")
            if is_match(cur_path):
                ret_path = cur_path
                break

            elif isinstance(value, dict):
                ret_path = get_complete_path(value, path, cur_path)
                if ret_path:
                    break

            elif isinstance(value, list):
                for i in range(len(value)):
                    ret_path = get_complete_path(value[i], path, "%s_%s" % (cur_path, str(i)))
                    if ret_path:
                        return ret_path

    elif isinstance(json_data, list):
        for i in range(len(json_data)):
            ret_path = get_complete_path(json_data[i], path, "%s_%s" % (base_path, str(i)))
            if ret_path:
                break

    return ret_path


def set_field_value(json_data, path, value):
    """
    set the value of the specified field in json data
    :param json_data:
    :param path:specify the field (hierarchical strings separated by _)
                please specify a unique field, if more than one is found, only change the first by default;
                if it's a list, you can add a list index, such as 'repayPlanInfo_0_sumAmount'
    :param value:
    :return: the modified json data

    example:
    json_data = {
        "repayPlanDetail": {
            "repayPlanInfo": [{
                "repayScheduleNo": "123141121212",
                "curEndDate": "123141121212",
                "sumAmount": 1200,
            }]
        }
    }

    set_field_value(json_data, "repayPlanDetail_repayPlanInfo_0_sumAmount", 600)
    """
    # call parse_json to get the complete format string
    complete_path = get_complete_path(json_data, path)

    if not complete_path:
        raise Exception("path error: %s" % path)

    formats = complete_path.split("_")
    obj, size = json_data, len(formats)

    for index in range(size):
        try:
            field = formats[index]
            field = int(field)
        except ValueError as e:
            pass

        if index == size - 1:
            obj[field] = value
        else:
            obj = obj[field]

    return json_data
