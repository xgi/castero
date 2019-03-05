import os
from shutil import copyfile

from castero.episode import Episode
from castero.feed import Feed
from castero.feedsdb import FeedsDB

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_feedsdb_from_json(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", FeedsDB.OLD_PATH)
    myfeedsdb = FeedsDB()

    feeds = myfeedsdb.feeds()
    assert len(feeds) == 2
    assert feeds[0].key == "feed key"
    assert feeds[0].title == "feed title"
    assert feeds[0].description == "feed description"
    assert feeds[0].link == "feed link"
    assert feeds[0].last_build_date == "feed last_build_date"
    assert feeds[0].copyright == "feed copyright"
    episodes0 = myfeedsdb.episodes(feeds[0])
    assert episodes0[0].title == "episode title"
    assert episodes0[0].description == "episode description"
    assert episodes0[0].link == "episode link"
    assert episodes0[0].pubdate == "episode pubdate"
    assert episodes0[0].copyright == "episode copyright"
    assert episodes0[0].enclosure == "episode enclosure"

    assert feeds[1].key == "http://feed2_url"
    assert feeds[1].title == "feed2 title"
    assert feeds[1].description == "feed2 description"
    assert feeds[1].link == "feed2 link"
    assert feeds[1].last_build_date == "feed2 last_build_date"
    assert feeds[1].copyright == "feed2 copyright"
    episodes1 = myfeedsdb.episodes(feeds[1])
    assert episodes1[0].title == "episode title"
    assert episodes1[0].description == "episode description"
    assert episodes1[0].link == "episode link"
    assert episodes1[0].pubdate == "episode pubdate"
    assert episodes1[0].copyright == "episode copyright"
    assert episodes1[0].enclosure == "episode enclosure"
