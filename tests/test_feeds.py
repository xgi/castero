import copy
import os
from shutil import copyfile
import castero.feeds as feeds
from castero.feed import Feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_feeds_default(prevent_modification):
    myfeeds = feeds.Feeds()
    assert isinstance(myfeeds, feeds.Feeds)


def test_feeds_write(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    myfeeds[myfeed_path] = myfeed
    myfeeds.write()
    myfeeds2 = feeds.Feeds()
    assert myfeed_path in myfeeds2


def test_feeds_length(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    assert type(len(myfeeds) == int) and len(myfeeds) == 2


def test_feeds_iter(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    for key in myfeeds:
        assert key in myfeeds


def test_feeds_get_item(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    myfeed = myfeeds["feed key"]
    assert isinstance(myfeed, Feed)


def test_feeds_set_item(prevent_modification):
    myfeeds = feeds.Feeds()
    myfeeds["fake"] = "value"
    assert "fake" in myfeeds


def test_feeds_del_item(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    del myfeeds["feed key"]
    assert "seek_distance" not in myfeeds


def test_feeds_at_0(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    assert myfeeds.at(0).title == "feed title"


def test_feeds_at_1(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    assert myfeeds.at(1).title == "feed2 title"


def test_feeds_at_2(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    assert myfeeds.at(2) is None


def test_feeds_del_at_0(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    deleted = myfeeds.del_at(0)
    assert deleted
    assert "feed key" not in myfeeds


def test_feeds_del_at_1(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    deleted = myfeeds.del_at(1)
    assert deleted
    assert "http://feed2_url" not in myfeeds


def test_feeds_del_at_2(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    deleted = myfeeds.del_at(2)
    assert not deleted


def test_feeds_reload(prevent_modification):
    os.chdir(my_dir)
    copyfile(my_dir + "/datafiles/feeds_working2", feeds.Feeds.PATH)
    myfeeds = feeds.Feeds()
    myfeeds2 = copy.copy(myfeeds)
    myfeeds2.reload()
    for feed in myfeeds:
        assert feed in myfeeds2
