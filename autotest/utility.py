# -*- coding: utf-8 -*-
import os
from datetime import date
from datetime import timedelta
import time
import shelve
import random
import collections
from copy import deepcopy
import sys

if sys.version_info[0] == 3:
    from autotest.lib.allthepairs.all_pairs2 import all_pairs2 as all_pairs
else:
    from metacomm.combinatorics.all_pairs2 import all_pairs2 as all_pairs


from faker import Factory
from faker.providers import BaseProvider
import inspect
from functools import wraps
from .lib.district_code import DistrictCode
import pyDes
from pyDes import triple_des
import base64


def advance_logger(loglevel):
    def get_line_number():
        return inspect.currentframe().f_back.f_back.f_lineno

    def _basic_log(fn, result, *args, **kwargs):
        print("function   = " + fn.__name__, end=' ')
        print("    arguments = {0} {1}".format(args, kwargs))
        print("    return    = {0}".format(result))

    def info_log_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            _basic_log(fn, result, args, kwargs)
            return result
        return wrapper

    def debug_log_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ts = time.time()
            result = fn(*args, **kwargs)
            te = time.time()
            _basic_log(fn, result, args, kwargs)
            print("    time      = %.6f sec" % (te - ts))
            print("    called_from_line : " + str(get_line_number()))
            return result
        return wrapper
    if loglevel is "debug":
        return debug_log_decorator
    else:
        return info_log_decorator


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


def des3_encrypt(key, ivect, text):
    cipher = triple_des(key, mode=pyDes.CBC, IV=ivect, padmode=pyDes.PAD_PKCS5)
    r = cipher.encrypt(text)
    return base64.standard_b64encode(r)


class MyProvider(BaseProvider):
    def _getDistrictCode(self):
        global state, city
        data = DistrictCode.CODES
        district_list = data.split('\n')
        code_list = []
        for node in district_list:
            if node[10:11] != ' ':
                state = node[10:].strip()
            if node[10:11] == ' ' and node[12:13] != ' ':
                city = node[12:].strip()
            if node[10:11] == ' ' and node[12:13] == ' ':
                district = node[14:].strip()
                code = node[0:6]
                code_list.append(
                    {"state": state, "city": city, "district": district,
                     "code": code})
        return code_list

    def create_id_card(self):
        code_list = self._getDistrictCode()
        id = code_list[random.randint(0, len(code_list) - 1)]['code']
        id = id + str(random.randint(1930, 1992))
        da = date.today() + timedelta(days=random.randint(1, 366))
        id = id + da.strftime('%m%d')
        id = id + str(random.randint(100, 999))
        count = 0
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        for i in range(0, 17):
            count = count + int(id[i]) * weight[i]
        id = id + '10X98765432'[count % 11]
        return id


@singleton
class Utility(object):

    def __init__(self):
        self.json_value_list = []
        self.fake_cn = Factory.create('zh_CN')
        self.fake_en = Factory.create()
        self.fake_cn.add_provider(MyProvider)

    def __getattr__(self, item):
        if item == 'fake':
            return self.fake_cn
        if item == 'gennerator':
            return self.fake_cn.create_id_card()

    @classmethod
    def intersection_of_path(self, file_path):
        relative_file_path = os.path.normpath(file_path)
        relative_list = relative_file_path.split(os.sep)
        sys_path_now_list = os.path.dirname(__file__).split(os.sep)[1:]
        for i in range(len(sys_path_now_list)):
            if (relative_list[0] == sys_path_now_list[i]): intersection = i
        prepose_path = ''.join(
            ['/%s' % y for y in sys_path_now_list[:intersection]])
        return os.path.join(prepose_path, file_path)

    @property
    def fakerUserTerInfo(self):
        return "%s|%s|PC|MAC|APP" % (
            self.fake.ipv4(),
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    @property
    def fake_email_safe(self):
        fake = Factory.create()
        return fake.free_email()

    @property
    def start_end_date(self):
        start_date = self.fake.date(pattern="%Y-%m-%d")
        return start_date, str(int(start_date[0:4]) + 10) + start_date[4:]

    @staticmethod
    def filter_dict(key, the_dict):
        keys = list(the_dict.keys())
        del keys[key.index(key)]
        [the_dict.pop(k) for k in keys]
        return the_dict

    def dict2obj(self, d):
        if isinstance(d, list):
            d = [self.dict2obj(x) for x in d]
        if not isinstance(d, dict):
            return d
        class C(object):
            pass
        o = C()
        for k in d:
            o.__dict__[k] = self.dict2obj(d[k])
        return o

    @staticmethod
    def save_data_shelve(path, name, data):
        database = shelve.open('%svars.db' % path, 'c')
        try:
            database[str(name)] = data
        finally:
            database.close()

    @staticmethod
    def get_data_shelve(path, name):
        database = shelve.open('%svars.db' % path, 'r')
        try:
            return database[str(name)]
        finally:
            database.close()

    def find_item_of_json(self, candidate, node, key, container):
        def add_to_container(source):
            if key:
                try:
                    if isinstance(source, list):
                        for i in source:
                            container.append(i[key])
                    else:
                        container.append(source[key])
                except KeyError:
                    pass
            else:
                container.append(source)
        if isinstance(candidate, dict):
            if node in candidate:
                sub_candidate = candidate[node]
                add_to_container(sub_candidate)
            else:
                for k in candidate:
                    self.find_item_of_json(candidate[k], node, key, container)
        elif isinstance(candidate, list):
            for i in candidate:
                self.find_item_of_json(i, node, key, container)

    @staticmethod
    def loop_check(func, *args, **kwargs):
        sleep_time = 1
        loop_time = 10
        for k in ['sleep_time', 'loop_time']:
            if k in kwargs:
                exec("%s = %s" % (k, kwargs[k]))
                kwargs.pop(k)
        times = 0
        while times < loop_time:
            time.sleep(sleep_time)
            flag = func(*args, **kwargs)
            if not isinstance(flag, bool):
                raise Exception("function return must be boll!")
            if flag:
                break
            else:
                times += 1
                print('*' * 10 + "The %s times loop check for the %s \n" % (
                    times, func.__name__))
        else:
            raise Exception("Tried %s times the %s Loop check failed." % (
                times, func.__name__))

    @staticmethod
    def all_pairs_format(parameters, mode='dict', rules=None):
        pk = list(parameters.keys())

        def reformat_parameters_for_list(pairwise_item):
            temp = deepcopy(parameters)
            for i in range(len(pairwise_item)):
                temp[pk[i]] = pairwise_item[i]
            return temp

        def reformat_parameters_for_dict(pairwise_item):
            temp = deepcopy(parameters)
            for k in range(len(pk)):
                temp[pk[k]] = [i[k] for i in pairwise_item]
            return temp

        def is_valid_combination(values, name, rules):
            dictionary = dict(list(zip(name, values)))
            for rule in rules:
                try:
                    if rule(dictionary):
                        return False
                except KeyError:
                    pass
            return True

        if isinstance(rules, collections.Callable):
            pairwise = all_pairs(list(parameters.values()),
                                 filter_func=rules)
        elif isinstance(rules, (list, tuple)):
            pairwise = all_pairs(list(parameters.values()),
                                 filter_func=lambda
                                     values: is_valid_combination(
                                     values, pk, rules))
        else:
            pairwise = all_pairs(list(parameters.values()))
        if mode == 'dict':
            return reformat_parameters_for_dict([v for v in pairwise])
        elif mode == 'list':
            return [reformat_parameters_for_list(v) for v in pairwise]
        else:
            raise Exception(
                "parameter mode is wrong, Please enter the correct parameter")


class Pipe(object):

    def __init__(self, func):
        self.func = func

    def __ror__(self, other):
        def generator():
            for obj in other:
                if obj is not None:
                    yield self.func(obj)
        return generator()
