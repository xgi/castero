import pytest
import os
from shutil import copyfile
import castero.config as config

my_dir = os.path.dirname(os.path.realpath(__file__))


def hide_user_config():
    """Moves the user's config file, if it exists, to make it unreachable.
    """
    if os.path.exists(config.Config.PATH):
        os.rename(config.Config.PATH, config.Config.PATH + ".tmp")


def restore_user_config():
    """Restores the user's config file if it has been hidden."""
    if os.path.exists(config.Config.PATH + ".tmp"):
        os.rename(config.Config.PATH + ".tmp", config.Config.PATH)


def test_config_default():
    hide_user_config()
    myconfig = config.Config()
    restore_user_config()
    assert isinstance(myconfig, config.Config)


def test_config_parse_error():
    hide_user_config()
    copyfile(my_dir + "/datafiles/parse_error.conf", config.Config.PATH)
    with pytest.raises(config.ConfigParseError):
        myconfig = config.Config()
    restore_user_config()


def test_config_incomplete_migrate():
    hide_user_config()
    copyfile(my_dir + "/datafiles/incomplete_error.conf", config.Config.PATH)
    myconfig = config.Config()
    assert len(myconfig) > 0
    restore_user_config()


def test_config_excessive_migrate():
    hide_user_config()
    copyfile(my_dir + "/datafiles/excessive_error.conf", config.Config.PATH)
    myconfig = config.Config()
    assert "this_should_not_be_here" not in myconfig
    assert "seek_distance" in myconfig
    restore_user_config()


def test_config_length():
    hide_user_config()
    myconfig = config.Config()
    restore_user_config()
    assert type(len(myconfig) == int) and len(myconfig) > 0


def test_config_iter():
    hide_user_config()
    myconfig = config.Config()
    restore_user_config()
    for key in myconfig:
        assert key in myconfig


def test_config_get_item():
    hide_user_config()
    myconfig = config.Config()
    restore_user_config()
    seek_distance = myconfig["seek_distance"]
    assert seek_distance is not None


def test_config_try_set_item():
    hide_user_config()
    myconfig = config.Config()
    myconfig["fake"] = "value"
    restore_user_config()
    assert "fake" not in myconfig


def test_config_del_item():
    hide_user_config()
    myconfig = config.Config()
    restore_user_config()
    del myconfig["seek_distance"]
    assert "seek_distance" not in myconfig
