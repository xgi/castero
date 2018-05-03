import vlc
import time


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
    """
    def __init__(self, title, path) -> None:
        """Initializes the object.

        Args:
            title: the title of the media (usually an episode title)
            path: a URL or file-path of a media file (usually an audio file)
        """
        assert type(title) == str and title != ""
        assert type(path) == str and path != ""

        self._title = title
        self._path = path
        self._media = None
        self._player = None
        self._duration = -1  # in milliseconds
        self._state = 0  # 0=stopped, 1=playing, 2=paused

    def __del__(self) -> None:
        if self._player is not None:
            self.stop()

    @staticmethod
    def check_dependencies():
        """Checks whether dependencies are met for playing a player.

        Raises:
            PlayerDependencyError: a dependency was not met
        """
        try:
            vlc.Instance()
        except NameError:
            raise PlayerDependencyError(
                "Dependency VLC not found, which is required for playing"
                " media files"
            )

    def _create_player(self) -> None:
        """Creates the VLC player object while making sure it is a valid file.

        Checks some basic properties of the file to ensure it will play
        properly, including:
            - the media object could be parsed
            - it has a duration > 0

        Raises:
            PlayerCreateError: the player object could not be created
        """
        vlc_instance = vlc.Instance("--no-video --quiet")

        self._player = vlc_instance.media_player_new()
        self._media = vlc_instance.media_new(self._path)
        self._media.parse()  # may output some junk into the console
        self._player.set_media(self._media)

        self._duration = self._media.get_duration()

    def play(self) -> None:
        """Plays the media.
        """
        if self._player is None:
            self._create_player()

        self._player.play()
        self._state = 1

    def stop(self) -> None:
        """Stops the media.
        """
        if self._player is not None:
            if self._player.get_state() == vlc.State.Opening:
                self._player.release()
            else:
                self._player.stop()
                self._state = 0

    def pause(self) -> None:
        """Pauses the media.
        """
        if self._player is not None:
            if self._player.get_state() != vlc.State.Opening:
                self._player.pause()
                self._state = 2

    def seek(self, direction, amount) -> None:
        """Seek forward or backward in the media.

        Args:
            direction: 1 to seek forward, -1 to seek backward
            amount: the amount of seconds to seek
        """
        assert direction == 1 or direction == -1
        if self._player is not None:
            self._player.set_time(
                self._player.get_time() + (direction * amount * 1000)
            )

    @property
    def state(self) -> int:
        """int: the state of the player"""
        return self._state

    @property
    def title(self) -> str:
        """str: the title of the player"""
        return self._title

    @property
    def duration(self) -> int:
        """int: the duration of the player"""
        result = 0
        if self._media is not None:
            self._duration = self._media.get_duration()
            result = self._duration
        return result

    @property
    def time(self) -> int:
        """int: the current time of the player"""
        if self._player is not None:
            return self._player.get_time()

    @property
    def time_str(self) -> str:
        """str: the formatted time and duration of the player"""
        result = "00:00:00/00:00:00"
        if self._player is not None:
            time_seconds = int(self.time / 1000)
            length_seconds = int(self.duration / 1000)
            t = time.strftime('%H:%M:%S', time.gmtime(time_seconds))
            d = time.strftime('%H:%M:%S', time.gmtime(length_seconds))
            result = "%s/%s" % (t, d)
        return result
