import re
from autotest import BaseServiceEntityHandler
from autotest import getCleanJsonView
from autotest import handle_item_in_json

BAISIC_URL_PATTERN = "http://%s"
PATH = '/braavos/api/swagger.json'
URL = BAISIC_URL_PATTERN + PATH
BODY_DATA = ''
QUERY_DATA = ''
METHOD_TYPE = 'get'
CONTENT_TYPE = ''
HAS_DATA_PATTERN = False
PARAMETER_TYPE_MAP_ARG_NAME = {'path': 'parameters_in_path',
                               'body': 'body_data',
                               'query': 'query_data',
                               'header': 'header'
                               }
UNWANTED_KEYS = ('default', 'type', 'uniqueItems', 'description', 'format')


def always_get_list(instance):
    return not isinstance(instance, list) and [instance] or instance


class SwaggerEntity(BaseServiceEntityHandler):
    def __init__(self, domain_name):
        super(SwaggerEntity, self).__init__(
            domain_name=domain_name,
            url_string=URL,
            method_type=METHOD_TYPE,
            request_content_type=CONTENT_TYPE,
            has_data_pattern=HAS_DATA_PATTERN)

        self._iter_paths = None
        self._current_scope = None
        self._full_json_content = None
        self._full_scope = 'full_scope'
        self._json_content_cache = {}
        self._current_root_ref_pair = {}
        self._recursive_depth_count = 0

    @property
    def iter_paths(self):
        if not self._json_content:
            return False
        if not self._iter_paths:
            self._iter_paths = iter(list(self.paths.keys()))
        return self._iter_paths

    @property
    def json_content_cache(self):
        return self._json_content_cache

    @property
    def current_root_ref_pair(self):
        return self._current_root_ref_pair

    def _clear_current_root_ref_pair(self):
        if self.current_root_ref_pair:
            self._current_root_ref_pair.clear()

    def _update_json_content_cache(self, scope, content):
        self._json_content_cache.update({scope: content})

    def _switch_json_content(self, scope, content=None, cached=True):
        if not self._current_scope == scope:
            if cached:
                if scope not in self.json_content_cache:
                    content = content or getattr(self, scope)
                    self._update_json_content_cache(scope, content)

                self._json_content = self.json_content_cache[scope]
            else:
                self._json_content = content or getattr(self, scope)

            if self._json_content:
                self._current_scope = scope

    def _reload_json_content(self):
        self._switch_json_content(self._full_scope, self._full_json_content)

    def send_request(self):
        try:
            super(SwaggerEntity, self).send_request()
        except Exception:
            pass

        self._full_json_content = self._json_content

    def __next__(self):
        try:
            def _switch_to_current_path_method_scope():
                self._reload_json_content()
                self._switch_json_content(scope_path)
                self._switch_json_content(method_type)

            def _switch_to_definition_scope():
                self._reload_json_content()
                self._switch_json_content(scope_definitions)

            def _switch_to_path_scope():
                self._reload_json_content()
                self._switch_json_content(scope_path)

            def _get_ref():
                ref_node = '$ref'
                refs = always_get_list(getattr(self, ref_node))

                if refs:
                    upper_layer_content = self._json_content
                    _values = []

                    for ref in refs:
                        definition_node = ref.split('#/definitions/')[1]

                        if not self.current_root_ref_pair:
                            self._current_root_ref_pair.update(
                                {'from': definition_node, 'to': None})
                        elif not self.current_root_ref_pair['to']:
                            self._current_root_ref_pair['to'] = definition_node
                        elif self.current_root_ref_pair['from'] == definition_node:
                            handle_item_in_json(candidate=upper_layer_content,
                                                node=ref_node,
                                                values=
                                                {'circular_reference': definition_node},
                                                mode='replace_key_with_value')
                            return

                        _switch_to_definition_scope()

                        definition_node_content = \
                            getattr(self, definition_node + '_properties')

                        if definition_node_content:
                            _values.append(
                                {definition_node: definition_node_content})

                            self._switch_json_content(definition_node,
                                                      definition_node_content,
                                                      cached=True)
                            self._recursive_depth_count += 1
                            _get_ref()
                            self._recursive_depth_count -= 1
                    if _values:
                        handle_item_in_json(candidate=upper_layer_content,
                                            node=ref_node, values=_values,
                                            mode='set')
                    if not self._recursive_depth_count:
                        self._clear_current_root_ref_pair()

            def _get_schema(source):
                schema = getattr(self, source)
                _get_ref()

                return schema

            def _get_parameters_name():
                index = next(indexes)
                name = always_get_list(self.name)[index]

                if parameters_enum or parameters_schema:
                    self._switch_json_content('parameter', parameters[index],
                                              cached=False)
                    if self.enum:
                        name_enum_pair = {name: {'enum': self.enum}}

                        return name_enum_pair

                    if self.schema:
                        schema = _get_schema('schema')
                        name_schema_pair = {'schema': schema}
                        return name_schema_pair

                return name

            def _get_responses():
                if self.responses_200:
                    schema_source = 'schema'

                    self._switch_json_content('responses_200', cached=False)

                    if self.schema_additionalProperties:
                        schema_source = 'schema_additionalProperties'

                    if self.schema_items:
                        schema_source = 'schema_items'

                    value = _get_schema(schema_source)

                    _switch_to_current_path_method_scope()

                    return value

            def _handle_parameters_in():
                value_for_oprate = None

                variable = parameter_type_map_variable[parameter_type]
                # dynamically getting operator depending on var type
                variable_oprator = \
                    isinstance(variable, list) and \
                    'append' or isinstance(variable, dict) and 'update'
                # get value by parameter type
                value_for_oprate = \
                    parameter_type_map_handle_func[parameter_type]()

                if value_for_oprate:
                    getattr(variable, variable_oprator)(value_for_oprate)

                    _key = PARAMETER_TYPE_MAP_ARG_NAME[parameter_type]
                    _inner_attr_map.update({_key: variable})

                    _switch_to_current_path_method_scope()

            entities_attr_map = {}
            entities_attr_map_key = None
            scope_path = next(self.iter_paths)
            cls_name = re.sub(r'[/{}-]', '', scope_path.title())
            scope_definitions = 'definitions'
            has_data_pattern = False
            content_type = None
            parameter_type_map_handle_func = {'path': _get_parameters_name,
                                              'query': _get_parameters_name,
                                              'body': _get_parameters_name,
                                              'header': _get_parameters_name
                                              }
            _switch_to_path_scope()

            for method_type in (
                        self.post and 'post',
                        self.get and 'get',
                        self.put and 'put',
                        self.delete and 'delete'):

                if not method_type:
                    continue

                _switch_to_current_path_method_scope()

                body_data = {}
                query_data = []
                response = None
                parameters_in_path = []
                schemes = None
                header = []
                parameter_type_map_variable = {'path': parameters_in_path,
                                               'query': query_data,
                                               'body': body_data,
                                               'header': header
                                               }
                _inner_attr_map = {}
                entities_attr_map_key = method_type + '_entity'
                # set content type value
                if self.consumes:
                    content_type = self.consumes[0]
                # parse parameter and get value
                # get value from path,query,body
                # and set value for parameters_in_path,query_data,body_data
                parameters_in = always_get_list(self.parameters_in)
                if parameters_in:
                    parameters = always_get_list(self.parameters)
                    parameters_enum = always_get_list(self.parameters_enum)
                    parameters_schema = always_get_list(self.parameters_schema)

                    indexes = iter([i for i in range(len(parameters_in))])

                    for parameter_type in parameters_in:
                        _handle_parameters_in()
                # set value for has_data_pattern
                if body_data or query_data:
                    has_data_pattern = True
                # set response
                response = _get_responses()
                # set schemes value
                if self.schemes:
                    schemes = self.schemes[0]

                miscellaneous_info = {'method_type': method_type,
                                      'has_data_pattern': has_data_pattern,
                                      'content_type': content_type,
                                      'cls_name': method_type.title() + cls_name,
                                      'path': scope_path,
                                      'response': response,
                                      'schemes': schemes
                                      }
                _inner_attr_map.update(miscellaneous_info)
                # replace ref tag for ref node with refferd item
                handle_item_in_json(candidate=_inner_attr_map,
                                    node='$ref', mode='replace_key_with_value',
                                    deep_search=True)
                # remove unwanted key in keys
                [
                    handle_item_in_json(candidate=_inner_attr_map,
                                        node=uk, mode='pop_key',
                                        deep_search=True)
                    for uk in UNWANTED_KEYS
                    ]

                entities_attr_map.update(
                    {entities_attr_map_key: _inner_attr_map})

            print(getCleanJsonView(entities_attr_map))
            print('++++++++++++++++++')
            return entities_attr_map
        except StopIteration:
            pass
        finally:
            [self._json_content_cache.pop(k)
             for k in ('get', 'post', 'put', 'delete')
             if k in self._json_content_cache]

            self._reload_json_content()


if __name__ == '__main__':
    e = SwaggerEntity('127.0.0.1')
    e.send_request()
    paths = e.paths

    for i in range(len(paths)):
        next(e)
        print(getCleanJsonView(list(e._json_content_cache.keys())))
        print('!!!!!!!!!!!!!!!!!!')
        # assert 0