import os
from unittest import mock

from castero.datafile import DataFile
from castero.downloadqueue import DownloadQueue
from castero.episode import Episode
from castero.feed import Feed

title = "episode title"
description = "episode description"
link = "episode link"
pubdate = "episode pubdate"
copyright = "episode copyright"
enclosure = "episode enclosure"

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_episode_init():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed,
                        title=title,
                        description=description,
                        link=link,
                        pubdate=pubdate,
                        copyright=copyright,
                        enclosure=enclosure)
    assert isinstance(myepisode, Episode)


def test_episode_properties():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed,
                        title=title,
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
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert isinstance(myepisode, Episode)


def test_episode_only_description():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, description=description)
    assert isinstance(myepisode, Episode)


def test_episode_str_title():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert str(myepisode) == title


def test_episode_str_description():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, description=description)
    assert str(myepisode) == description


def test_episode_missing_property_title():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, description=description)
    assert myepisode.title == "Title not available."


def test_episode_missing_property_description():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert myepisode.description == "Description not available."


def test_episode_missing_property_link():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert myepisode.link == "Link not available."


def test_episode_missing_property_pubdate():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert myepisode.pubdate == "Publish date not available."


def test_episode_missing_property_copyright():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert myepisode.copyright == "No copyright specified."


def test_episode_missing_property_enclosure():
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = Episode(myfeed, title=title)
    assert myepisode.enclosure == "Enclosure not available."


def test_episode_playable_remote():
    myfeed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
    episode = myfeed.parse_episodes()[0]
    playable = episode.get_playable()
    assert not episode.downloaded
    assert playable == "http://example.com/myfeed_item1_title.mp3"


def test_episode_playable_local():
    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(my_dir, "downloaded")
    myfeed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
    episode = myfeed.parse_episodes()[0]
    playable = episode.get_playable()
    assert episode.downloaded
    assert playable == os.path.join(DataFile.DEFAULT_DOWNLOADED_DIR,
                                    "myfeed_title",
                                    "myfeed_item1_title.mp3")

    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(DataFile.DATA_DIR,
                                                   "downloaded")


def test_episode_delete(display):
    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(my_dir, "downloaded")
    episode_location = os.path.join(DataFile.DEFAULT_DOWNLOADED_DIR,
                                    "myfeed_title/myfeed_item2_title.mp3")
    with open(episode_location, "w") as file:
        file.write("temp file for test_episode.test_episode_delete")
    myfeed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
    display.change_status = mock.MagicMock(name="change_status")
    episode = myfeed.parse_episodes()[1]
    assert episode.downloaded
    episode.delete(display=display)
    assert display.change_status.call_count == 1
    assert not episode.downloaded

    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(DataFile.DATA_DIR,
                                                   "downloaded")


def test_episode_download():
    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(my_dir, "downloaded")
    mydownloadqueue = DownloadQueue()
    myfeed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
    myepisode = myfeed.parse_episodes()[1]
    DataFile.download_to_file = mock.MagicMock(name="download_to_file")
    myepisode.download(mydownloadqueue)
    assert DataFile.download_to_file.call_count == 1

    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(DataFile.DATA_DIR,
                                                   "downloaded")


def test_episode_download_with_display(display):
    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(my_dir, "downloaded")
    mydownloadqueue = DownloadQueue()
    myfeed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
    myepisode = myfeed.parse_episodes()[1]
    DataFile.download_to_file = mock.MagicMock(name="download_to_file")
    display.change_status = mock.MagicMock(name="change_status")
    myepisode.download(mydownloadqueue, display=display)
    assert DataFile.download_to_file.call_count == 1

    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(DataFile.DATA_DIR,
                                                   "downloaded")


def test_episode_download_with_display_no_enclosure(display):
    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(my_dir, "downloaded")
    mydownloadqueue = DownloadQueue()
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    myepisode = myfeed.parse_episodes()[1]
    DataFile.download_to_file = mock.MagicMock(name="download_to_file")
    display.change_status = mock.MagicMock(name="change_status")
    myepisode.download(mydownloadqueue, display=display)
    assert display.change_status.call_count == 1

    DataFile.DEFAULT_DOWNLOADED_DIR = os.path.join(DataFile.DATA_DIR,
                                                   "downloaded")
