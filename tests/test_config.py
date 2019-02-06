import configparser
import os
from shutil import copyfile
from unittest import mock
from unittest.mock import patch, mock_open

import pytest

import castero.config as config

my_dir = os.path.dirname(os.path.realpath(__file__))

config_default_path = config._Config.DEFAULT_PATH


@pytest.fixture(autouse=True)
def restore_default_path():
    yield
    config._Config.DEFAULT_PATH = config_default_path


def test_config_default():
    myconfig = config._Config()
    assert isinstance(myconfig, config._Config)


def test_config_parse_error():
    config._Config.DEFAULT_PATH = my_dir + "/datafiles/parse_error.conf"
    with pytest.raises(config.ConfigParseError):
        config._Config()


def test_config_incomplete_migrate():
    copyfile(my_dir + "/datafiles/incomplete_error.conf", config._Config.PATH)
    myconfig = config._Config()
    assert len(myconfig) > 0


def test_config_excessive_migrate():
    copyfile(my_dir + "/datafiles/excessive_error.conf", config._Config.PATH)
    myconfig = config._Config()
    assert "this_should_not_be_here" not in myconfig
    assert "seek_distance" in myconfig


def test_config_length():
    myconfig = config._Config()
    assert type(len(myconfig) == int) and len(myconfig) > 0


def test_config_iter():
    myconfig = config._Config()
    for key in myconfig:
        assert key in myconfig


def test_config_get_item():
    myconfig = config._Config()
    seek_distance = myconfig["seek_distance"]
    assert seek_distance is not None


def test_config_try_set_item():
    myconfig = config._Config()
    myconfig["fake"] = "value"
    assert "fake" not in myconfig


def test_config_del_item():
    myconfig = config._Config()
    del myconfig["seek_distance"]
    assert "seek_distance" not in myconfig


def test_migrate_stability():
    conf = configparser.ConfigParser()
    default_conf = configparser.ConfigParser()
    default_conf.read(config._Config.DEFAULT_PATH)
    conf.read(my_dir + "/datafiles/working_no_comments.conf")

    conf.read = mock.MagicMock()

    with patch("builtins.open", mock_open(read_data="test")) as mock_file:
        config.Config.migrate(conf, default_conf)
        mock_file.assert_called_with(config.Config.DEFAULT_PATH, 'w')
