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


def test_player_mpv_check_dependencies():
    assert MPVPlayer.check_dependencies


def test_player_mpv_init():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert isinstance(myplayer, MPVPlayer)


def test_player_mpv_play():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.play()
    assert myplayer.state == 1


def test_player_mpv_pause():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.pause()
    assert myplayer.state == 2


def test_player_mpv_stop():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.stop()
    assert myplayer.state == 0


def test_player_mpv_del():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert "myplayer" in locals()
    del myplayer
    assert "myplayer" not in locals()


def test_player_mpv_seek():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.seek(1, 10)
    myplayer._player.seek.assert_called_with(10)


def test_player_mpv_set_rate():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.set_rate(1.6)
    assert myplayer._player.speed == 1.6


def test_player_mpv_str():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert str(myplayer) == "[%s] %s" % (episode.feed_str, myplayer.title)


def test_player_mpv_title():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert myplayer.title == "player1 title"


def test_player_mpv_episode():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    assert myplayer.episode == episode


def test_player_mpv_time():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer._player.time_pos = 5
    assert myplayer.time == 5000


def test_player_mpv_time_str():
    myplayer = MPVPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()
    myplayer._media = mock.MagicMock()

    myplayer._player.time_pos = 2
    assert myplayer.time_str == "00:00:02/00:00:01"
