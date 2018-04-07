import os
import pytest
import castero.feed as feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_feed_validation_valid():
    myfeed = feed.Feed(file=my_dir+"/feeds/valid_basic.xml")
    assert isinstance(myfeed, feed.Feed)


def test_feed_validations_is_rss():
    with pytest.raises(feed.FeedStructureError):
        myfeed = feed.Feed(file=my_dir+"/feeds/broken_is_rss.xml")


def test_feed_validations_is_v2():
    with pytest.raises(feed.FeedStructureError):
        myfeed = feed.Feed(file=my_dir+"/feeds/broken_is_v2.xml")


def test_feed_validations_has_channel():
    with pytest.raises(feed.FeedStructureError):
        myfeed = feed.Feed(file=my_dir+"/feeds/broken_has_channel.xml")


def test_feed_validations_channel_children():
    with pytest.raises(feed.FeedStructureError):
        myfeed = feed.Feed(file=my_dir+"/feeds/broken_channel_children.xml")


def test_feed_validations_two_channels():
    with pytest.raises(feed.FeedStructureError):
        myfeed = feed.Feed(file=my_dir+"/feeds/broken_two_channels.xml")


def test_feed_validations_item_title():
    with pytest.raises(feed.FeedStructureError):
        myfeed = feed.Feed(file=my_dir+"/feeds/broken_item_title.xml")
