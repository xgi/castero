import os

import vlc

from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed
from castero.player import Player
from castero.queue import Queue

my_dir = os.path.dirname(os.path.realpath(__file__))

config = Config()
feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
episode = Episode(feed,
                  title="episode title",
                  description="episode description",
                  link="episode link",
                  pubdate="episode pubdate",
                  copyright="episode copyright",
                  enclosure="episode enclosure")
player1 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3", episode)
player2 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3", episode)
player3 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3", episode)


def test_queue_init():
    myqueue = Queue(config)
    assert isinstance(myqueue, Queue)


def test_queue_first():
    myqueue = Queue(config)
    myqueue.add(player1)
    assert myqueue.first == player1


def test_queue_get():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.add(player2)
    retrieved_player1 = myqueue[0]
    assert retrieved_player1 == player1
    retrieved_player2 = myqueue[1]
    assert retrieved_player2 == player2


def test_queue_add():
    myqueue = Queue(config)
    myqueue.add(player1)
    assert myqueue.length == 1


def test_queue_length():
    myqueue = Queue(config)
    assert myqueue.length == 0
    myqueue.add(player1)
    assert myqueue.length == 1
    myqueue.add(player2)
    assert myqueue.length == 2
    myqueue.add(player3)
    assert myqueue.length == 3


def test_queue_clear():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.add(player2)
    assert myqueue.length == 2
    myqueue.clear()
    assert myqueue.length == 0


def test_queue_remove():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.add(player2)
    assert myqueue.length == 2
    removed_index = myqueue.remove(player1)
    assert removed_index == 0
    assert myqueue.length == 1
    assert myqueue.first == player2


def test_queue_next():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.add(player2)
    assert myqueue.length == 2
    myqueue.next()
    assert myqueue.length == 1
    assert myqueue.first.state == 1
    myqueue.stop()


def test_queue_play():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.play()
    while player1._player.get_state() != vlc.State.Playing:
        pass
    assert player1.state == 1
    myqueue.stop()


def test_queue_pause():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.play()
    while player1._player.get_state() != vlc.State.Playing:
        pass
    myqueue.pause()
    assert player1.state == 2
    myqueue.stop()


def test_queue_stop():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.play()
    while player1._player.get_state() != vlc.State.Playing:
        pass
    myqueue.stop()
    assert player1.state == 0


def test_queue_toggle():
    myqueue = Queue(config)
    myqueue.add(player1)
    assert player1.state == 0
    myqueue.toggle()
    while player1._player.get_state() != vlc.State.Playing:
        pass
    assert player1.state == 1
    myqueue.toggle()
    assert player1.state == 2
    myqueue.stop()


def test_queue_seek():
    myqueue = Queue(config)
    myqueue.add(player1)
    myqueue.play()
    while player1._player.get_state() != vlc.State.Playing:
        pass
    myqueue.seek(1)
    assert player1.time == int(config["seek_distance"]) * 1000
    myqueue.stop()
