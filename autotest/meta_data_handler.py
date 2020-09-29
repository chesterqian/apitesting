import json
from contextlib import contextmanager
import re
from .lib.json_handler import handle_item_in_json
from .lib.json_handler import getCleanJsonView
from .exception import MetaDataException

ERROR_MSG = "invalid meta data!"
ERROR_MSG2 = """The attribute, named: {}, don't suitable for getting in this way.
                (may should in _special_node_attributes or _special_key_attributes?)"""


class JsonHandlerMixin(object):
    def __getattr__(self, attribute):
        """
        The method can help to get the entity attribute value in json object.
        And no declaration is needed in the entity.
        There are some requirements have to meet for the attribute name:
        i. the name should be combined with 'node name'+'_'+'key name' of the attribute in json object;
        ii. if 'node name' includes '_', the attribute name has to be added in special_node_attributes.
        iii. if 'key name' includes '_', the attribute name has to be added in special_key_attributes.
        :param attribute: the attribute name
        :return: the value which is corresponding to the given attribute name in json object.
        """
        if self.meta_data:
            if attribute in self.data_content_cache:
                return self.data_content_cache[attribute]
            else:
                values = []
                node, key = self._get_json_value_by_node_key(attribute)
                handle_item_in_json(self.meta_data, node, key, values)

                if len(values) == 1:
                    values = values.pop()

                self._update_data_content_cache(attribute, values)

                return values
        else:
            raise MetaDataException(ERROR_MSG)

    def __setattr__(self, attribute, value):
        """
        The method can help to set the entity attribute value in json object.
        And no declaration is needed in the entity.
        There are some requirements have to meet for the attribute name:
        i. the name should be combined with 'node name'+'_'+'key name' of the attribute in json object;
        ii. if 'node name' includes '_', the attribute name has to be added in special_node_attributes.
        iii. if 'key name' includes '_', the attribute name has to be added in special_key_attributes.
        :param attribute: the attribute name
        :return: will set the value of which is corresponding to the given attribute name in json object.
        """
        if hasattr(self, attribute) and self.data_content_cache and \
                        attribute in self.data_content_cache:
            if self.meta_data:
                node, key = self._get_json_value_by_node_key(attribute)
                handle_item_in_json(self.meta_data, node, key, values=value,
                                    mode='set')

                self.data_content_cache.pop(attribute)
                self._update_data_content_cache(attribute,
                                                getattr(self, attribute))
            else:
                raise MetaDataException(ERROR_MSG)
        else:
            super(JsonHandlerMixin, self).__setattr__(attribute, value)

    def __str__(self):
        return getCleanJsonView(self.meta_data)

    def _get_json_value_by_node_key(self, attribute):
        node, key = None, None
        should_raise_exception = False

        sign_count = attribute.count('_')
        if sign_count <= 1 and attribute not in self._special_node_attributes:
            raw_list = attribute.split('_')
            if len(raw_list) == 1:
                node, key = attribute, None
            elif len(raw_list) == 2:
                node, key = raw_list[0], raw_list[1]
            else:
                should_raise_exception = True
        elif 1 <= sign_count <= 2:
            for i in self._special_node_attributes:
                if attribute.startswith(i):
                    node = i
                    if sign_count == 1:
                        key = attribute.replace(i, '')
                    else:
                        key = attribute.replace(i + '_', '')
                    break
            if not (node or key):
                for i in self._special_key_attributes:
                    if attribute.endswith(i):
                        node = attribute.replace('_' + i, '')
                        key = i
                        break

        if not (node or key):
            should_raise_exception = True

        if should_raise_exception:
            raise MetaDataException(ERROR_MSG2.format(attribute))

        return node, key


class BaseMetaDataHandler(JsonHandlerMixin):
    _meta_data = None
    _special_node_attributes = None
    _special_key_attributes = None
    _full_data_content = None
    _current_scope = None
    _data_content_cache = None
    _data_content_cache_history = None
    _full_data_content_str = None
    _full_scope = None

    def __init__(self, meta):
        self._data_content_cache = {}
        self._data_content_cache_history = {}
        self._special_key_attributes = []
        self._special_node_attributes = []

        if isinstance(meta, str):
            self._full_data_content_str = meta
            self._meta_data = json.loads(meta)
        elif isinstance(meta, dict) or isinstance(meta, list):
            self._meta_data = meta
            self._full_data_content_str = json.dumps(meta)

        self._handle_underling_attr()

        self._full_data_content = self._meta_data
        self._full_scope = 'full_scope'

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
            content = content if content is not None else getattr(self, scope)
            if cached:
                if scope not in self.data_content_cache:
                    self._update_data_content_cache(scope, content)

                self._meta_data = self.data_content_cache[scope]
            else:
                self._meta_data = content
            if self._meta_data is not None:
                self._current_scope = scope

            self._data_content_cache.clear()

    def _handle_underling_attr(self):
        p = '''([A-Z a-z])\w+_([A-Z a-z])\w+'''
        s = self._full_data_content_str
        attrs = []
        for i in re.finditer(p, s):
            attrs.append(i.group())

        self._special_node_attributes = self._special_key_attributes = attrs

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
