import os
from castero.episode import Episode
from castero.feed import Feed
from castero.datafile import DataFile

title = "episode title"
description = "episode description"
link = "episode link"
pubdate = "episode pubdate"
copyright = "episode copyright"
enclosure = "episode enclosure"

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_episode_init():
    myepisode = Episode(title=title,
                        description=description,
                        link=link,
                        pubdate=pubdate,
                        copyright=copyright,
                        enclosure=enclosure)
    assert isinstance(myepisode, Episode)


def test_episode_properties():
    myepisode = Episode(title=title,
                        description=description,
                        link=link,
                        pubdate=pubdate,
                        copyright=copyright,
                        enclosure=enclosure)
    assert myepisode.title == title
    assert myepisode.description == description
    assert myepisode.link == link
    assert myepisode.pubdate == pubdate
    assert myepisode.copyright == copyright
    assert myepisode.enclosure == enclosure


def test_episode_only_title():
    myepisode = Episode(title=title)
    assert isinstance(myepisode, Episode)


def test_episode_only_description():
    myepisode = Episode(description=description)
    assert isinstance(myepisode, Episode)


def test_episode_str_title():
    myepisode = Episode(title=title)
    assert str(myepisode) == title


def test_episode_str_description():
    myepisode = Episode(description=description)
    assert str(myepisode) == description


def test_episode_missing_property_title():
    myepisode = Episode(description=description)
    assert myepisode.title == "Title not available."


def test_episode_missing_property_description():
    myepisode = Episode(title=title)
    assert myepisode.description == "Description not available."


def test_episode_missing_property_link():
    myepisode = Episode(title=title)
    assert myepisode.link == "Link not available."


def test_episode_missing_property_pubdate():
    myepisode = Episode(title=title)
    assert myepisode.pubdate == "Publish date not available."


def test_episode_missing_property_copyright():
    myepisode = Episode(title=title)
    assert myepisode.copyright == "Copyright not available."


def test_episode_missing_property_enclosure():
    myepisode = Episode(title=title)
    assert myepisode.enclosure == "Enclosure not available."


def test_episode_playable_remote():
    myfeed = Feed(file=my_dir+"/feeds/valid_enclosures.xml")
    playable = myfeed.episodes[0].get_playable(myfeed)
    assert playable == "http://example.com/myfeed_item1_title.mp3"


def test_episode_playable_local():
    DataFile.DOWNLOADED_DIR = os.path.join(my_dir, "downloaded")
    myfeed = Feed(file=my_dir+"/feeds/valid_enclosures.xml")

    playable = myfeed.episodes[0].get_playable(myfeed)
    assert playable == os.path.join(DataFile.DOWNLOADED_DIR, "myfeed_title",
                                    "myfeed_item1_title.mp3")