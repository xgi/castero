import os
from shutil import copyfile

import pytest

import castero.config as config

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_config_default(prevent_modification):
    myconfig = config._Config()
    assert isinstance(myconfig, config._Config)


def test_config_parse_error(prevent_modification):
    copyfile(my_dir + "/datafiles/parse_error.conf", config._Config.PATH)
    with pytest.raises(config._ConfigParseError):
        config._Config()


def test_config_incomplete_migrate(prevent_modification):
    copyfile(my_dir + "/datafiles/incomplete_error.conf", config._Config.PATH)
    myconfig = config._Config()
    assert len(myconfig) > 0


def test_config_excessive_migrate(prevent_modification):
    copyfile(my_dir + "/datafiles/excessive_error.conf", config._Config.PATH)
    myconfig = config._Config()
    assert "this_should_not_be_here" not in myconfig
    assert "seek_distance" in myconfig


def test_config_length(prevent_modification):
    myconfig = config._Config()
    assert type(len(myconfig) == int) and len(myconfig) > 0


def test_config_iter(prevent_modification):
    myconfig = config._Config()
    for key in myconfig:
        assert key in myconfig


def test_config_get_item(prevent_modification):
    myconfig = config._Config()
    seek_distance = myconfig["seek_distance"]
    assert seek_distance is not None


def test_config_try_set_item(prevent_modification):
    myconfig = config._Config()
    myconfig["fake"] = "value"
    assert "fake" not in myconfig


def test_config_del_item(prevent_modification):
    myconfig = config._Config()
    del myconfig["seek_distance"]
    assert "seek_distance" not in myconfig
