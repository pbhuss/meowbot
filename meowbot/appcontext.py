import yaml
from flask import g

YAML_CONF_PATH = 'instance/config.yaml'


def get_config():
    if 'config' not in g:
        with open(YAML_CONF_PATH, 'r') as fp:
            g.config = yaml.load(fp)
    return g.config
