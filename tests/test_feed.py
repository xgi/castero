import os

import pytest

import castero.feed as feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_feed_validation_valid():
    myfeed = feed.Feed(file=my_dir + "/feeds/valid_basic.xml")
    assert isinstance(myfeed, feed.Feed)
    assert myfeed.validated
    assert len(myfeed.parse_episodes()) == 3


def test_feed_validation_complete():
    myfeed = feed.Feed(file=my_dir + "/feeds/valid_complete.xml")
    assert isinstance(myfeed, feed.Feed)
    assert myfeed.validated
    assert len(myfeed.parse_episodes()) == 3


def test_feed_validation_valid_mixed_enclosure():
    myfeed = feed.Feed(file=my_dir + "/feeds/valid_mixed_enclosures.xml")
    assert isinstance(myfeed, feed.Feed)
    assert myfeed.validated
    assert len(myfeed.parse_episodes()) == 2


def test_feed_validations_is_rss():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_is_rss.xml")


def test_feed_validations_is_v2():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_is_v2.xml")


def test_feed_validations_rss_empty():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_rss_empty.xml")


def test_feed_validations_has_channel():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_has_channel.xml")


def test_feed_validations_channel_children():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_channel_children.xml")


def test_feed_validations_channel_empty():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_channel_empty.xml")


def test_feed_validations_two_channels():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_two_channels.xml")


def test_feed_validations_item_title():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_item_title.xml")


def test_feed_validations_no_version():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_no_version.xml")


def test_feed_validations_extra_link():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_extra_link.xml")


def test_feed_validations_extra_description():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_extra_description.xml")


def test_feed_validations_no_channel():
    with pytest.raises(feed.FeedStructureError):
        feed.Feed(file=my_dir + "/feeds/broken_no_channel.xml")


def test_feed_download_error():
    with pytest.raises(feed.FeedDownloadError):
        feed.Feed(url="http://notreal")


def test_feed_load_error():
    with pytest.raises(feed.FeedLoadError):
        feed.Feed(file="notreal")
