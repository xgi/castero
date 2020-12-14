import os
from shutil import copyfile
from unittest import mock

from castero.episode import Episode
from castero.feed import Feed
from castero.database import Database

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_database_default(prevent_modification):
    mydatabase = Database()
    assert isinstance(mydatabase, Database)


def test_database_feeds_length(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    assert len(mydatabase.feeds()) == 2


def test_database_feed(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    feed = mydatabase.feeds()[0]
    assert isinstance(feed, Feed)
    assert feed.key == "feed key"
    assert feed.title == "feed title"


def test_database_feed_episodes(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    feed = mydatabase.feeds()[0]
    episodes = mydatabase.episodes(feed)
    for episode in episodes:
        assert isinstance(episode, Episode)


def test_database_episode_id(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    episode = mydatabase.episode(1)
    assert episode.ep_id == 1
    assert episode.title == "episode title"


def test_database_episodes_length(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    feed1 = mydatabase.feeds()[0]
    feed2 = mydatabase.feeds()[1]
    assert len(mydatabase.episodes(feed1)) == 1
    assert len(mydatabase.episodes(feed2)) == 1


def test_database_feed_unplayed_episode_length(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()
    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    episodes = myfeed.parse_episodes()

    mydatabase.replace_feed(myfeed)
    mydatabase.replace_episode(myfeed, episodes[0])
    mydatabase.replace_episode(myfeed, episodes[1])
    assert len(mydatabase.unplayed_episodes(myfeed)) == 2
    feed_episodes = mydatabase.episodes(myfeed)
    feed_episodes[0].played = 1
    mydatabase.replace_episode(myfeed, feed_episodes[0])
    assert len(mydatabase.unplayed_episodes(myfeed)) == 1


def test_database_add_feed(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)

    assert len(mydatabase.feeds()) == 2
    mydatabase.replace_feed(myfeed)
    assert len(mydatabase.feeds()) == 3


def test_database_replace_feed(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed1 = Feed(file=myfeed_path)
    myfeed2 = Feed(file=myfeed_path)

    mydatabase.replace_feed(myfeed1)
    assert len(mydatabase.feeds()) == 3
    mydatabase.replace_feed(myfeed2)
    assert len(mydatabase.feeds()) == 3


def test_database_add_episode(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    episodes = myfeed.parse_episodes()

    mydatabase.replace_feed(myfeed)
    assert len(mydatabase.episodes(myfeed)) == 0
    mydatabase.replace_episode(myfeed, episodes[0])
    assert len(mydatabase.episodes(myfeed)) == 1


def test_database_replace_episode(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    episodes = myfeed.parse_episodes()

    mydatabase.replace_feed(myfeed)
    mydatabase.replace_episode(myfeed, episodes[0])
    assert len(mydatabase.episodes(myfeed)) == 1
    episode = mydatabase.episodes(myfeed)[0]
    mydatabase.replace_episode(myfeed, episode)
    assert len(mydatabase.episodes(myfeed)) == 1


def test_database_add_episodes(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()

    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    episodes = myfeed.parse_episodes()

    mydatabase.replace_feed(myfeed)
    assert len(mydatabase.episodes(myfeed)) == 0
    mydatabase.replace_episodes(myfeed, episodes)
    assert len(mydatabase.episodes(myfeed)) == len(episodes)


def test_database_add_episode_progress(prevent_modification):
    copyfile(my_dir + "/datafiles/database_example1.db", Database.PATH)
    mydatabase = Database()
    ep = mydatabase.episode(1)
    mydatabase.replace_progress(ep, 1000)
    ep_db = mydatabase.episode(1)
    assert ep_db.progress == 1000
    assert ep.progress == 1000


def test_database_reload(prevent_modification, display):
    mydatabase = Database()

    myfeed_path = my_dir + "/feeds/valid_basic.xml"
    myfeed = Feed(file=myfeed_path)
    real_title = myfeed.title
    myfeed._title = "fake title"

    mydatabase.replace_feed(myfeed)

    display.change_status = mock.MagicMock(name="change_status")
    mydatabase.reload(display)
    assert display.change_status.call_count == 2
    assert mydatabase.feeds()[0].title == real_title


def test_database_from_json(prevent_modification):
    copyfile(my_dir + "/datafiles/feeds_working", Database.OLD_PATH)
    mydatabase = Database()

    feeds = mydatabase.feeds()
    assert len(feeds) == 2

    # we don't technically make any assumptions about the order of the feeds
    if feeds[0].key != "feed key":
        feeds.reverse()

    assert feeds[0].key == "feed key"
    assert feeds[0].title == "feed title"
    assert feeds[0].description == "feed description"
    assert feeds[0].link == "feed link"
    assert feeds[0].last_build_date == "feed last_build_date"
    assert feeds[0].copyright == "feed copyright"
    episodes0 = mydatabase.episodes(feeds[0])
    assert episodes0[0].title == "episode title"
    assert episodes0[0].description == "episode description"
    assert episodes0[0].link == "episode link"
    assert episodes0[0].pubdate == "episode pubdate"
    assert episodes0[0].copyright == "episode copyright"
    assert episodes0[0].enclosure == "episode enclosure"
    assert not episodes0[0].played

    assert feeds[1].key == "http://feed2_url"
    assert feeds[1].title == "feed2 title"
    assert feeds[1].description == "feed2 description"
    assert feeds[1].link == "feed2 link"
    assert feeds[1].last_build_date == "feed2 last_build_date"
    assert feeds[1].copyright == "feed2 copyright"
    episodes1 = mydatabase.episodes(feeds[1])
    assert episodes1[0].title == "episode title"
    assert episodes1[0].description == "episode description"
    assert episodes1[0].link == "episode link"
    assert episodes1[0].pubdate == "episode pubdate"
    assert episodes1[0].copyright == "episode copyright"
    assert episodes1[0].enclosure == "episode enclosure"
    assert not episodes1[0].played
