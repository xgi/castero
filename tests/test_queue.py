import os
from unittest import mock

import vlc

from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed
from castero.queue import Queue
from castero.player import Player

my_dir = os.path.dirname(os.path.realpath(__file__))

feed = Feed(file=my_dir + "/feeds/valid_basic.xml")


def test_queue_init():
    myqueue = Queue(Config)
    assert isinstance(myqueue, Queue)


def test_queue_first():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    assert myqueue.first == player1


def test_queue_get():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)
    player2 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.add(player2)
    retrieved_player1 = myqueue[0]
    assert retrieved_player1 == player1
    retrieved_player2 = myqueue[1]
    assert retrieved_player2 == player2


def test_queue_add():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)

    myqueue = Queue(Config)
    myqueue.add(player1)
    assert myqueue.length == 1


def test_queue_length():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)
    player2 = mock.MagicMock(spec=Player)
    player3 = mock.MagicMock(spec=Player)

    assert myqueue.length == 0
    myqueue.add(player1)
    assert myqueue.length == 1
    myqueue.add(player2)
    assert myqueue.length == 2
    myqueue.add(player3)
    assert myqueue.length == 3


def test_queue_clear():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)
    player2 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.add(player2)
    assert myqueue.length == 2
    myqueue.clear()
    assert myqueue.length == 0


def test_queue_remove():
    player1 = mock.MagicMock(spec=Player)
    player2 = mock.MagicMock(spec=Player)

    myqueue.add(player2)
    assert myqueue.length == 2
    removed_index = myqueue.remove(player1)
    assert removed_index == 0
    assert myqueue.length == 1
    assert myqueue.first == player2


def test_queue_next():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)
    player2 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.add(player2)
    assert myqueue.length == 2
    myqueue.next()
    assert myqueue.length == 1


def test_queue_play():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.play()
    player1.play.assert_called_once()


def test_queue_pause():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.pause()
    player1.pause.assert_called_once()


def test_queue_stop():
    player1 = mock.MagicMock(spec=Player)

    myqueue.stop()
    player1.stop.assert_called_once()


def test_queue_toggle():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.toggle()
    player1.play.assert_called_once()
    player1.state = 1
    myqueue.toggle()
    player1.pause.assert_called_once()


def test_queue_seek():
    myqueue = Queue(Config)
    player1 = mock.MagicMock(spec=Player)

    myqueue.add(player1)
    myqueue.seek(1)
    player1.seek.assert_called_with(1, int(config["seek_distance"]))
    assert player1.time == int(Config["seek_distance"]) * 1000
    myqueue.stop()
