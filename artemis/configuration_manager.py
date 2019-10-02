from flask import config as flask_conf
import os
import logging.config
import sys

# by laziness we use flask config manager since it is the best we know
config = flask_conf.Config(os.path.dirname(os.path.realpath(__file__)))

config.from_object("artemis.default_settings")
if "CONFIG_FILE" in os.environ:
    config.from_envvar("CONFIG_FILE")

if "LOGGER" in config:
    logging.config.dictConfig(config["LOGGER"])
else:  # Default is std out
    handler = logging.StreamHandler(stream=sys.stdout)
    log = logging.getLogger(__name__)
    log.setLevel("INFO")
    log.addHandler(handler)
