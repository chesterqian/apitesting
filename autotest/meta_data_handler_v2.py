import json
from contextlib import contextmanager
import re
from .json_handler_v2 import search_keys, SpecialKeys
from .exception import MetaDataException

ERROR_MSG = "invalid meta data!"
ERROR_MSG2 = """The attribute, named: {}, don't suitable for getting in this way.
                (may should in _special_node_attributes or _special_key_attributes?)"""


class BaseMetaDataHandler(object):

    def __init__(self, meta):
        var_list = ['_meta_data', '_full_data_content', '_current_scope',
                    '_data_content_cache', '_data_content_cache_history',
                    '_full_data_content_str', '_full_scope', 'special_keys']
        self.declare_vars(var_list)
        self._data_content_cache = {}
        self._data_content_cache_history = {}

        if isinstance(meta, str):
            self._full_data_content_str = meta
            self._meta_data = json.loads(meta)
        elif isinstance(meta, dict) or isinstance(meta, list):
            self._meta_data = meta
            self._full_data_content_str = json.dumps(meta)

        self.special_keys = SpecialKeys(self._meta_data)

        self._full_data_content = self._meta_data
        self._full_scope = 'full_scope'

    def declare_vars(self, var_list):
        for v in var_list:
            super().__setattr__(v, None)

    @property
    def meta_data(self):
        return self._meta_data

    @property
    def data_content_cache(self):
        return self._data_content_cache

    def _update_data_content_cache(self, scope, content):
        d = {scope: content}
        self._data_content_cache.update(d)
        self._data_content_cache_history.update(d)

    def _switch_data_content(self, scope, content=None, cached=True):
        if not self._current_scope == scope:
            content = content if content is not None else getattr(self,
                                                                  scope)
            if cached:
                if scope not in self.data_content_cache:
                    self._update_data_content_cache(scope, content)

                self._meta_data = self.data_content_cache[scope]
            else:
                self._meta_data = content
            if self._meta_data is not None:
                self._current_scope = scope

            self._data_content_cache.clear()

    def switch_to_full_data_content(self):
        self._switch_data_content(self._full_scope, self._full_data_content)

    def reload_full_data_content(self):
        self._meta_data = json.loads(self._full_data_content_str)
        self._data_content_cache.clear()

    @contextmanager
    def shift_context(self, scope, content=None, cached=True,
                      back_to_scope=None, back_to_content=None,
                      *args, **kwargs):
        # args: (scope, content=None, cached=True)
        self._switch_data_content(scope, content, cached, *args, **kwargs)
        yield
        if not back_to_content:
            self.switch_to_full_data_content()
        else:
            self._switch_data_content(back_to_scope, back_to_content)

    def __getattr__(self, attribute):
        # print("Get", attribute)
        if attribute in dir(self):
            super().__getattr__(attribute)
        elif self.meta_data:
            if attribute in self.data_content_cache:
                return self.data_content_cache[attribute]
            else:
                keys = self._get_keys(attribute)
                values = search_keys(self.meta_data, keys)

                if len(values) == 1:
                    values = values.pop()
                elif not values:
                    values = None

                self._update_data_content_cache(attribute, values)

                return values
        else:
            print("Get Error")

    def __setattr__(self, attribute, value):
        # print("Set", attribute)
        if attribute in dir(self):
            super().__setattr__(attribute, value)
        elif self.meta_data:
            keys = self._get_keys(attribute)
            r = search_keys(self.meta_data, keys,
                        replace=True,
                        set_value=value)
            if not r:
                raise MetaDataException(ERROR_MSG)
            if attribute in self.data_content_cache:
                self.data_content_cache.pop(attribute)
        else:
            super().__setattr__(attribute, value)

    def __str__(self):
        return json.dumps(self.meta_data, indent=2)

    def _get_keys(self, attribute):
        keys = self.special_keys.parse(attribute)
        return keys


if __name__ == "__main__":
    d = {
        "id": 123
    }
    mdh = BaseMetaDataHandler(d)
    print(mdh.id)
