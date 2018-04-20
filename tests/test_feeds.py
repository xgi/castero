import copy
import os
from shutil import copyfile
import castero.feeds as feeds
from castero.feed import Feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def hide_user_feeds():
    """Moves the user's feeds file, if it exists, to make it unreachable.
    """
    if os.path.exists(feeds.Feeds.PATH):
        os.rename(feeds.Feeds.PATH, feeds.Feeds.PATH + ".tmp")


def restore_user_feeds():
    """Restores the user's feeds file if it has been hidden."""
    if os.path.exists(feeds.Feeds.PATH + ".tmp"):
        os.rename(feeds.Feeds.PATH + ".tmp", feeds.Feeds.PATH)


def test_feeds_default():
    hide_user_feeds()
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    assert isinstance(myfeeds, feeds.Feeds)


def test_feeds_write():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    myfeeds[myfeed_path] = myfeed
    myfeeds.write()
    myfeeds2 = feeds.Feeds()
    restore_user_feeds()
    assert myfeed_path in myfeeds2


def test_feeds_length():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    assert type(len(myfeeds) == int) and len(myfeeds) == 2


def test_feeds_iter():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    for key in myfeeds:
        assert key in myfeeds


def test_feeds_get_item():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    myfeed = myfeeds["feed key"]
    assert isinstance(myfeed, Feed)


def test_feeds_set_item():
    hide_user_feeds()
    myfeeds = feeds.Feeds()
    myfeeds["fake"] = "value"
    restore_user_feeds()
    assert "fake" in myfeeds


def test_feeds_del_item():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    del myfeeds["feed key"]
    assert "seek_distance" not in myfeeds


def test_feeds_at_0():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    assert myfeeds.at(0).title == "feed title"


def test_feeds_at_1():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    assert myfeeds.at(1).title == "feed2 title"


def test_feeds_at_2():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    assert myfeeds.at(2) is None


def test_feeds_del_at_0():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    deleted = myfeeds.del_at(0)
    assert deleted
    assert "feed key" not in myfeeds


def test_feeds_del_at_1():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    deleted = myfeeds.del_at(1)
    assert deleted
    assert "http://feed2_url" not in myfeeds


def test_feeds_del_at_2():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    restore_user_feeds()
    deleted = myfeeds.del_at(2)
    assert not deleted


def test_feeds_reload_1():
    hide_user_feeds()
    copyfile(my_dir + "/datafiles/feeds_working2", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    myfeeds2 = copy.copy(myfeeds)
    myfeeds2.reload()
    restore_user_feeds()
    for feed in myfeeds:
        assert feed in myfeeds2
