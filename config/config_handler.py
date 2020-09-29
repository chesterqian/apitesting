import os
import json
from autotest.meta_data_handler import BaseMetaDataHandler


def get_json():
    current_dir = os.path.dirname(__file__)
    print(current_dir)
    with open(os.path.join(current_dir, "config.json")) as f:
        json = f.read()
        return json


class ConfigParser:
    config_handler = None

    @classmethod
    def parse(cls):
        configs = json.loads(get_json())
        test_env = os.environ.get("test_env", configs["test_env"])
        if not test_env:
            raise Exception("Error!!! No Test Env Specified!!!")
        if test_env not in configs:
            raise Exception("Error!!! Test Env {} Not Found!!!".format(
                test_env))
        cls.config_handler = BaseMetaDataHandler(configs[test_env])


# load only once
if not ConfigParser.config_handler:
    ConfigParser.parse()
config_handler = ConfigParser.config_handler

# print(config_handler.apiHost)