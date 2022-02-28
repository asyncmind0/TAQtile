from system import default_config, get_hostconfig, get_hostconfig_dict
import yaml


def test_get_default_config():
    print(yaml.dump(default_config))


def test_get_hostconfig():
    print(yaml.dump(get_hostconfig_dict()))
