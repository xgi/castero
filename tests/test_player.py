import os

import vlc

import castero.player as player
from castero.episode import Episode
from castero.feed import Feed

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
    assert player.Player.check_dependencies


def test_player_init():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    assert isinstance(myplayer, player.Player)


def test_player_play():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    myplayer.play()
    while myplayer._player.get_state() == vlc.State.Opening:
        pass
    assert myplayer.state == 1


def test_player_pause():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    myplayer.play()
    while myplayer._player.get_state() != vlc.State.Playing:
        pass
    myplayer.pause()
    assert myplayer.state == 2


def test_player_stop():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    myplayer.play()
    while myplayer._player.get_state() != vlc.State.Playing:
        pass
    myplayer.stop()
    assert myplayer.state == 0


def test_player_del():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    assert "myplayer" in locals()
    del myplayer
    assert "myplayer" not in locals()


def test_player_seek():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    myplayer.play()
    while myplayer._player.get_state() != vlc.State.Playing:
        pass
    myplayer.seek(1, 10)
    assert myplayer.time == 10 * 1000


def test_player_title():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    assert myplayer.title == "MLK Dream"


def test_player_time():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    myplayer.play()
    while myplayer._player.get_state() != vlc.State.Playing:
        pass
    assert myplayer.time == 0


def test_player_time_str():
    myplayer = player.Player("MLK Dream", my_dir + "/media/MLK_Dream_10s.mp3",
                             episode)
    myplayer.play()
    while myplayer._player.get_state() != vlc.State.Playing:
        pass
    assert myplayer.time_str == "00:00:00/00:00:05"
