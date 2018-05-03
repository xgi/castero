from unittest import mock
import os
from castero.downloadqueue import DownloadQueue
from castero.feed import Feed
from castero.episode import Episode

my_dir = os.path.dirname(os.path.realpath(__file__))

feed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
episode1 = Episode(feed=feed, title="episode1 title")
episode2 = Episode(feed=feed, title="episode2 title")


def test_downloadqueue_init():
    mydownloadqueue = DownloadQueue()
    assert isinstance(mydownloadqueue, DownloadQueue)


def test_downloadqueue_add():
    mydownloadqueue = DownloadQueue()
    assert mydownloadqueue.length == 0
    mydownloadqueue.add(episode1)
    assert mydownloadqueue.length == 1
    mydownloadqueue.add(episode1)
    assert mydownloadqueue.length == 1
    mydownloadqueue.add(episode2)
    assert mydownloadqueue.length == 2


def test_downloadqueue_start():
    mydownloadqueue = DownloadQueue()
    mydownloadqueue.add(episode1)
    episode1.download = mock.MagicMock(name="download")
    mydownloadqueue.start()
    episode1.download.assert_called_with(mydownloadqueue, None)


def test_downloadqueue_first():
    mydownloadqueue = DownloadQueue()
    mydownloadqueue.add(episode1)
    assert mydownloadqueue.first == episode1


def test_downloadqueue_next():
    mydownloadqueue = DownloadQueue()
    mydownloadqueue.add(episode1)
    mydownloadqueue.add(episode2)
    mydownloadqueue.start = mock.MagicMock(name="start")
    mydownloadqueue.next()
    assert mydownloadqueue.length == 1
    mydownloadqueue.start.assert_called_once()


def test_downloadqueue_update():
    mydownloadqueue = DownloadQueue()
    mydownloadqueue.add(episode1)
    mydownloadqueue.start = mock.MagicMock(name="start")
    mydownloadqueue.update()
    mydownloadqueue.start.assert_called_once()
