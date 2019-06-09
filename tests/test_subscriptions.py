import os
from unittest import mock
import xml.etree.ElementTree as ElementTree

import pytest

from castero.feed import Feed
from castero.subscriptions import Subscriptions, SubscriptionsLoadError, \
    SubscriptionsParseError, SubscriptionsStructureError, SubscriptionsError

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_subscriptions_valid_complete():
    mysubscriptions = Subscriptions()
    Feed.__init__ = mock.MagicMock(return_value=None)
    mysubscriptions.load(my_dir + "/subscriptions/valid_complete.xml")
    assert isinstance(mysubscriptions, Subscriptions)
    Feed.__init__.assert_any_call(url="http://feed1")
    Feed.__init__.assert_any_call(url="http://feed2")
    assert Feed.__init__.call_count == 2
    assert len(mysubscriptions.feeds) == 2


def test_subscriptions_valid_no_head():
    mysubscriptions = Subscriptions()
    Feed.__init__ = mock.MagicMock(return_value=None)
    mysubscriptions.load(my_dir + "/subscriptions/valid_no_head.xml")
    assert isinstance(mysubscriptions, Subscriptions)
    Feed.__init__.assert_any_call(url="http://feed1")
    Feed.__init__.assert_any_call(url="http://feed2")
    assert Feed.__init__.call_count == 2
    assert len(mysubscriptions.feeds) == 2


def test_subscriptions_valid_minimal():
    mysubscriptions = Subscriptions()
    Feed.__init__ = mock.MagicMock(return_value=None)
    mysubscriptions.load(my_dir + "/subscriptions/valid_minimal.xml")
    assert isinstance(mysubscriptions, Subscriptions)
    assert len(mysubscriptions.feeds) == 0


def test_subscriptions_broken_nonexistant():
    mysubscriptions = Subscriptions()
    Feed.__init__ = mock.MagicMock(return_value=None)
    with pytest.raises(SubscriptionsLoadError):
        mysubscriptions.load(my_dir + "/subscriptions/doesnt_exist")


def test_subscriptions_broken_parse():
    mysubscriptions = Subscriptions()
    Feed.__init__ = mock.MagicMock(return_value=None)
    with pytest.raises(SubscriptionsParseError):
        mysubscriptions.load(my_dir + "/subscriptions/broken_parse.xml")


def test_subscriptions_broken_no_body():
    mysubscriptions = Subscriptions()
    Feed.__init__ = mock.MagicMock(return_value=None)
    with pytest.raises(SubscriptionsStructureError):
        mysubscriptions.load(my_dir + "/subscriptions/broken_no_body.xml")


def test_subscriptions_generate():
    feed1 = mock.MagicMock()
    feed2 = mock.MagicMock()
    mysubscriptions = Subscriptions()
    mysubscriptions.generate([feed1, feed2])

    Feed.__init__ = mock.MagicMock(return_value=None)
    mysubscriptions._parse_feeds()
    assert len(mysubscriptions.feeds) == 2


def test_subscriptions_save():
    temp_fname = my_dir + "/subscriptions/saved_temp.xml"
    Feed.__init__ = mock.MagicMock(return_value=None)

    mysubscriptions1 = Subscriptions()
    mysubscriptions1.load(my_dir + "/subscriptions/valid_complete.xml")
    mysubscriptions1.save(temp_fname)

    mysubscriptions2 = Subscriptions()
    mysubscriptions2.load(my_dir + "/subscriptions/saved_temp.xml")
    os.remove(temp_fname)

    tree1 = ElementTree.tostring(mysubscriptions1._tree.getroot())
    tree2 = ElementTree.tostring(mysubscriptions2._tree.getroot())
    assert tree1 == tree2


def test_subscriptions_save_before_create():
    mysubscriptions = Subscriptions()
    with pytest.raises(SubscriptionsError):
        mysubscriptions.save(my_dir + "/subscriptions/saved_bad_temp.xml")
