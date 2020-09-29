from pprint import pprint


def search_key(data, key, replace=False, set_value=None):
    ret = list()
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                ret.append(v)
                if replace:
                    data[key] = set_value
            else:
                r = search_key(v, key, replace, set_value)
                if r:
                    ret.extend(r)
    elif isinstance(data, list):
        for i in data:
            r = search_key(i, key, replace, set_value)
            if r:
                ret.extend(r)
    return ret


def search_keys(data, keys, replace=False, set_value=None):
    tmp = list()
    source_list = [data]
    length = len(keys)
    for index, key in enumerate(keys):
        for src in source_list:
            if index == length - 1:
                r = search_key(src, key, replace=replace, set_value=set_value)
            else:
                r = search_key(src, key, replace=False, set_value=set_value)

            if r:
                tmp.extend(r)
        source_list = tmp
        tmp = list()
    return source_list


class SpecialKeys:
    alias_format = "SpecialKeysZZZ-{}"

    def __init__(self, data):
        self.data = data
        self.special_keys = set()
        self.collect_special_keys(self.data)
        self.key_alias_map = dict()
        self.alias_key_map = dict()
        self.init_analysis_data()

    def collect_special_keys(self, data):
        if isinstance(data, dict):
            for k, v in data.items():
                if k.find("_") > -1 and k not in self.special_keys:
                    self.special_keys.add(k)
                else:
                    self.collect_special_keys(v)
        elif isinstance(data, list):
            for i in data:
                self.collect_special_keys(i)

    def init_analysis_data(self):
        for i, k in enumerate(self.special_keys):
            alias = self.alias_format.format(i)
            self.key_alias_map[k] = alias
            self.alias_key_map[alias] = k

    def parse(self, url):
        for k, a in self.key_alias_map.items():
            url = url.replace(k, a)
        keys = url.split("_")
        for i, k in enumerate(keys):
            if k in self.alias_key_map:
                keys[i] = self.alias_key_map[k]
        return keys


if __name__ == "__main__":
    d = {
        "a": "a",
        "b": {
            "b1": "b1",
            "b2": {
                "b_21": "b21",
                "b_22": "b22"
            }
        },
        "c": {
            "b2": {
                "c1": "c1"
            }
        },
        "d": [
            {
                "dd": [
                    {
                        "ddd_1": 1,
                        "ddd_2": 1
                    }
                ]
            },
            {
                "dd": [
                    {
                        "ddd_1": 2,
                        "ddd_2": 2
                    }
                ]
            },
            {
                "dd": 3
            }
        ]
    }
    # pprint(d)
    # pprint(search_key(d, "b2"))
    # pprint(search_keys(d, ["b", "b2"]))
    # pprint(search_key(d, "ddd1"))
    pprint(search_keys(d, ["d", "dd"]))
    pprint(search_keys(d, ["d", "dd", "ddd_1"], replace=True, set_value="HHHHH"))
    # pprint(d)
    pprint(search_keys(d, ["d", "dd", "ddd_1"]))

    sk = SpecialKeys(d)
    print(sk.special_keys)
    print(sk.parse("d_dd_ddd_1"))