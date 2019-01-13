import os
from unittest import mock

from castero.episode import Episode
from castero.feed import Feed
from castero.players.vlcplayer import VLCPlayer

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
    assert VLCPlayer.check_dependencies


def test_player_init():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert isinstance(myplayer, VLCPlayer)


def test_player_play():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.play()
    myplayer._player.play.assert_called_once()
    assert myplayer.state == 1


def test_player_pause():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.pause()
    myplayer._player.pause.assert_called_once()
    assert myplayer.state == 2


def test_player_stop():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.stop()
    myplayer._player.stop.assert_called_once()
    assert myplayer.state == 0


def test_player_del():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert "myplayer" in locals()
    del myplayer
    assert "myplayer" not in locals()


def test_player_seek():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.seek(1, 10)
    myplayer._player.set_time.assert_called_with(
        myplayer._player.get_time() + 10 * 1000)


def test_player_str():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert str(myplayer) == myplayer.title


def test_player_title():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert myplayer.title == "player1 title"


def test_player_episode():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert myplayer.episode == episode


def test_player_time():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer._player.get_time = mock.MagicMock(return_value=5000)
    assert myplayer.time == 5000


def test_player_time_str():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()
    myplayer._media = mock.MagicMock()

    myplayer._player.get_time = mock.MagicMock(return_value=3000)
    myplayer._media.get_duration = mock.MagicMock(return_value=6000)
    assert myplayer.time_str == "00:00:03/00:00:06"
