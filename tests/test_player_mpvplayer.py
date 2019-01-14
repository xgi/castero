import os
from unittest import mock

from castero.episode import Episode
from castero.feed import Feed
from castero.players.mpvplayer import MPVPlayer

my_dir = os.path.dirname(os.path.realpath(__file__))

feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
episode = Episode(feed,
                  title="episode title",
                  description="episode description",
                  link="episode link",
                  pubdate="episode pubdate",
                  copyright="episode copyright",
                  enclosure="episode enclosure")


def test_player_check_dependencies():
    assert MPVPlayer.check_dependencies


def test_player_init():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert isinstance(myplayer, MPVPlayer)


def test_player_play():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.play()
    myplayer._player.set_property.assert_called_with('pause', False)
    assert myplayer.state == 1


def test_player_pause():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.pause()
    myplayer._player.set_property.assert_called_with('pause', True)
    assert myplayer.state == 2


def test_player_stop():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.stop()
    myplayer._player.shutdown.assert_called_once()
    assert myplayer.state == 0


def test_player_del():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert "myplayer" in locals()
    del myplayer
    assert "myplayer" not in locals()


def test_player_seek():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.seek(1, 10)
    myplayer._player.command.assert_called_with('seek', 10)


def test_player_str():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert str(myplayer) == myplayer.title


def test_player_title():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert myplayer.title == "player1 title"


def test_player_episode():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert myplayer.episode == episode


def test_player_time():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer._player.get_property = mock.MagicMock(return_value=5)
    assert myplayer.time == 5000


def test_player_time_str():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()
    myplayer._media = mock.MagicMock()

    myplayer._player.get_property = mock.MagicMock(return_value=5)
    assert myplayer.time_str == "00:00:05/00:00:05"
