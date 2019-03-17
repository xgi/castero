import os
from unittest import mock

import pytest
import castero.config
from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed
from castero.player import Player, PlayerDependencyError, PlayerCreateError

my_dir = os.path.dirname(os.path.realpath(__file__))

feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
episode = Episode(feed,
                  title="episode title",
                  description="episode description",
                  link="episode link",
                  pubdate="episode pubdate",
                  copyright="episode copyright",
                  enclosure="episode enclosure")
SomePlayer = mock.MagicMock()
available_players = {
    "someplayer": SomePlayer
}


@pytest.fixture(autouse=True)
def restore_config_data():
    yield
    Config.data = castero.config._Config().data


def test_player_create_instance_success_direct():
    Config.data = {'player': 'someplayer'}
    myplayer = Player.create_instance(available_players, "t", "p", episode)
    SomePlayer.check_dependencies.assert_called_once()
    SomePlayer.assert_called_with("t", "p", episode)


def test_player_create_instance_success_indirect():
    Config.data = {'player': ''}
    myplayer = Player.create_instance(available_players, "t", "p", episode)
    SomePlayer.check_dependencies.assert_called = 2
    SomePlayer.assert_called_with("t", "p", episode)


def test_player_create_instance_dep_error_direct():
    Config.data = {'player': 'someplayer'}
    SomePlayer.check_dependencies.side_effect = PlayerDependencyError()
    with pytest.raises(PlayerDependencyError):
        myplayer = Player.create_instance(available_players, "t", "p", episode)
        SomePlayer.check_dependencies.assert_called_once()


def test_player_create_instance_dep_error_indirect():
    Config.data = {'player': ''}
    SomePlayer.check_dependencies.side_effect = PlayerDependencyError()
    with pytest.raises(PlayerDependencyError):
        myplayer = Player.create_instance(available_players, "t", "p", episode)
        SomePlayer.check_dependencies.assert_called_once()
