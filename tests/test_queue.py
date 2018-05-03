import os
import vlc
from castero.queue import Queue
from castero.player import Player
from castero.config import Config

my_dir = os.path.dirname(os.path.realpath(__file__))

config = Config()
player1 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3")
player2 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3")
player3 = Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3")


def test_queue_init():
    myqueue = Queue(config)
    assert isinstance(myqueue, Queue)


def test_queue_first():
    myqueue = Queue(config)
    myqueue.add(player1)
    assert myqueue.first == player1


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
