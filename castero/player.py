from abc import abstractmethod

import castero
from castero.config import Config
from castero.episode import Episode


class PlayerError(Exception):
    """An ambiguous error while handling the player.
    """


class PlayerDependencyError(PlayerError):
    """A dependency for playing the player was not met."""


class PlayerCreateError(PlayerError):
    """An error occurred while creating the player.
    """


class Player:
    """The Player class.

    This class is extended by players -- classes which offer methods to handle
    media operations for a specific external player (i.e. VLC, mpv).
    """

    def __init__(self, title, path, episode) -> None:
        """Initializes the object.

        Args:
            title: the title of the media (usually an episode title)
            path: a URL or file-path of a media file (usually an audio file)
            episode: the Episode which this is a player for
        """
        assert isinstance(title, str) and title != ""
        assert isinstance(path, str) and path != ""
        assert isinstance(episode, Episode) and episode is not None

        self._title = title
        self._path = path
        self._episode = episode
        self._media = None
        self._player = None
        self._duration = -1  # in milliseconds
        self._state = 0  # 0=stopped, 1=playing, 2=paused

    def __del__(self) -> None:
        if self._player is not None:
            self.stop()

    def __str__(self) -> str:
        """Represent this object as a string.

        Returns:
            string: the name of the feed and the title of the player
        """
        return "[%s] %s" % (self._episode.feed_str, self._title)

    @staticmethod
    def create_instance(available_players, title, path, episode):
        """Create an instance of an appropriate Player subclass.

        This method attempts to create a player based on the user's config
        option. If their option is not a key in available_players or
        check_dependencies() fails on the instance, we instead try to
        initialize the first working player using the order defined in
        available_players.

        Args:
            available_players: a list of implemented Player subclasses
            title: the title of the media (usually an episode title)
            path: a URL or file-path of a media file (usually an audio file)
            episode: the Episode which this is a player for

        Raises:
            PlayerDependencyError: at least one dependency per player for all
            players was not met
        """
        if Config["player"] in available_players:
            try:
                available_players[Config["player"]].check_dependencies()
                inst = available_players[Config["player"]](title, path,
                                                           episode)
                return inst
            except PlayerDependencyError:
                pass

        # Config had a bad/unsupported value; we'll instead try all implemented
        # options in order
        for av_player in sorted(available_players):
            try:
                available_players[av_player].check_dependencies()
                inst = available_players[av_player](title, path, episode)
                return inst
            except PlayerDependencyError:
                pass

        raise PlayerDependencyError("Sufficient dependencies were not met for"
                                    " any players. If you recently downloaded"
                                    " a player, you may need to reinstall %s"
                                    % castero.__title__)

    @staticmethod
    @abstractmethod
    def check_dependencies():
        """Checks whether dependencies are met for playing a player.

        Raises:
            PlayerDependencyError: a dependency was not met
        """

    @abstractmethod
    def _create_player(self) -> None:
        """Creates the player object while making sure it is a valid file.

        Checks some basic properties of the file to ensure it will play
        properly, including:
            - the media object could be parsed
            - it has a duration > 0

        Raises:
            PlayerCreateError: the player object could not be created
        """

    @abstractmethod
    def play(self) -> None:
        """Plays the media.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stops the media.
        """

    @abstractmethod
    def pause(self) -> None:
        """Pauses the media.
        """

    @abstractmethod
    def seek(self, direction, amount) -> None:
        """Seek forward or backward in the media.

        Args:
            direction: 1 to seek forward, -1 to seek backward
            amount: the amount of seconds to seek
        """

    @property
    def state(self) -> int:
        """int: the state of the player"""
        return self._state

    @property
    def title(self) -> str:
        """str: the title of the player"""
        return self._title

    @property
    def episode(self) -> Episode:
        """Episode: the Episode which this player has the media for"""
        return self._episode

    @property
    @abstractmethod
    def duration(self) -> int:
        """int: the duration of the player, in ms"""

    @property
    @abstractmethod
    def time(self) -> int:
        """int: the current time of the player, in ms"""

    @property
    @abstractmethod
    def time_str(self) -> str:
        """str: the formatted time and duration of the player"""
