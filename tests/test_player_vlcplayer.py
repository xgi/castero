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


def test_player_vlc_check_dependencies():
    assert VLCPlayer.check_dependencies


def test_player_vlc_init():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert isinstance(myplayer, VLCPlayer)


def test_player_vlc_play():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.play()
    assert myplayer._player.play.call_count == 1
    assert myplayer.state == 1


def test_player_vlc_pause():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.pause()
    assert myplayer._player.pause.call_count == 1
    assert myplayer.state == 2


def test_player_vlc_stop():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.stop()
    assert myplayer._player.stop.call_count == 1
    assert myplayer.state == 0


def test_player_vlc_del():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert "myplayer" in locals()
    del myplayer
    assert "myplayer" not in locals()


def test_player_vlc_seek():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.seek(1, 10)
    myplayer._player.set_time.assert_called_with(
        myplayer._player.get_time() + 10 * 1000)


def test_player_vlc_play_from():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()
    myplayer.play_from(10)

    assert myplayer._player.play.call_count == 1
    assert myplayer.state == 1
    myplayer._player.set_time.assert_called_with(10 * 1000)


def test_player_vlc_change_rate_increase():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer.set_rate(1.6)
    assert myplayer._player.set_rate.call_count == 1

def test_player_vlc_str():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert str(myplayer) == "[%s] %s" % (episode.feed_str, myplayer.title)


def test_player_vlc_title():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert myplayer.title == "player1 title"


def test_player_vlc_episode():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    assert myplayer.episode == episode


def test_player_vlc_time():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()

    myplayer._player.get_time = mock.MagicMock(return_value=5000)
    assert myplayer.time == 5000


def test_player_vlc_time_str():
    myplayer = VLCPlayer("player1 title", "player1 path", episode)
    myplayer._player = mock.MagicMock()
    myplayer._media = mock.MagicMock()

    myplayer._player.get_time = mock.MagicMock(return_value=3000)
    myplayer._media.get_duration = mock.MagicMock(return_value=6000)
    assert myplayer.time_str == "00:00:03/00:00:06"
