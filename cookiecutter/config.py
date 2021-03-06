# -*- coding: utf-8 -*-

"""
cookiecutter.config
-------------------

Global configuration handling
"""

from __future__ import unicode_literals
import copy
import logging
import os
import io

import poyo

from .exceptions import ConfigDoesNotExistException
from .exceptions import InvalidConfiguration


logger = logging.getLogger(__name__)

USER_CONFIG_PATH = os.path.expanduser('~/.cookiecutterrc')

DEFAULT_CONFIG = {
    'cookiecutters_dir': os.path.expanduser('~/.cookiecutters/'),
    'replay_dir': os.path.expanduser('~/.cookiecutter_replay/'),
    'default_context': {}
}


def _expand_path(path):
    """Expand both environment variables and user home in the given path."""
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    return path


def get_config(config_path):
    """
    Retrieve the config from the specified path, returning it as a config dict.
    """

    if not os.path.exists(config_path):
        raise ConfigDoesNotExistException

    logger.debug('config_path is {0}'.format(config_path))
    with io.open(config_path, encoding='utf-8') as file_handle:
        try:
            yaml_dict = poyo.parse_string(file_handle.read())
        except poyo.exceptions.PoyoException as e:
            raise InvalidConfiguration(
                'Unable to parse YAML file {}. Error: {}'
                ''.format(config_path, e)
            )

    config_dict = copy.copy(DEFAULT_CONFIG)
    config_dict.update(yaml_dict)

    raw_replay_dir = config_dict['replay_dir']
    config_dict['replay_dir'] = _expand_path(raw_replay_dir)

    raw_cookies_dir = config_dict['cookiecutters_dir']
    config_dict['cookiecutters_dir'] = _expand_path(raw_cookies_dir)

    return config_dict


def get_user_config(config_file=USER_CONFIG_PATH):
    """Retrieve the config from a file or return the defaults if None is
    passed. If an environment variable `COOKIECUTTER_CONFIG` is set up, try
    to load its value. Otherwise fall back to a default file or config.
    """
    # Do NOT load a config. Return defaults instead.
    if config_file is None:
        return copy.copy(DEFAULT_CONFIG)

    # Load the given config file
    if config_file and config_file is not USER_CONFIG_PATH:
        return get_config(config_file)

    try:
        # Does the user set up a config environment variable?
        env_config_file = os.environ['COOKIECUTTER_CONFIG']
    except KeyError:
        # Load an optional user config if it exists
        # otherwise return the defaults
        if os.path.exists(USER_CONFIG_PATH):
            return get_config(USER_CONFIG_PATH)
        else:
            return copy.copy(DEFAULT_CONFIG)
    else:
        # There is a config environment variable. Try to load it.
        # Do not check for existence, so invalid file paths raise an error.
        return get_config(env_config_file)
