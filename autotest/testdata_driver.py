import requests
import json

from tools.testdata_generator.testdata_gen.testdata_gen_lib import testdata_gen


def load_api_def(json_file_path):
    api_def = []
    with open(json_file_path, 'r') as fd:
        data = fd.read()
        api_def = json.loads(data)
        return api_def


def get_testdata(api_def, **kwargs):
    mode = kwargs.get('mode', 'mini')
    server = kwargs.get('server', None)
    if server:
        return _get_testdata_from_server(api_def, server, mode)
    else:
        return _get_testdata_from_lib(api_def, mode)


def _get_testdata_from_server(api_def, server='http://127.0.0.1:8000', mode='mini'):
    testdata_gen_server = server
    r = requests.post('{}/gen/{}'.format(testdata_gen_server, mode), json=api_def)
    return json.loads(r.content)


def _get_testdata_from_lib(api_def, mode='mini'):
    testdata = testdata_gen(api_def, mode='mini')
    return testdata
