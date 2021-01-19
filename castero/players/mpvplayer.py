from castero.player import Player, PlayerDependencyError
from castero import helpers, constants


class MPVPlayer(Player):
    """Interface for the mpv media player.
    """
    NAME = "mpv"

    def __init__(self, title, path, episode) -> None:
        """
        Overrides method from Player; see documentation in that class.
        """
        super().__init__(title, path, episode)

        import mpv
        self.mpv = mpv

    @staticmethod
    def check_dependencies():
        """Checks whether dependencies are met for playing a player.

        Overrides method from Player; see documentation in that class.
        """
        try:
            import mpv
            mpv.MPV()
        except (ImportError, NameError, OSError, AttributeError):
            raise PlayerDependencyError(
                "Dependency mpv not found, which is required for playing"
                " media files"
            )

    def _create_player(self) -> None:
        """Creates the player object while making sure it is a valid file.

        Overrides method from Player; see documentation in that class.
        """
        self._player = self.mpv.MPV()
        self._player.vid = False
        self._player.pause = False

        self._duration = 5

    def play(self) -> None:
        """Plays the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is None:
            self._create_player()

        self._player.play(self._path)

        self._player.pause = False
        self._state = 1

    def play_from(self, seconds) -> None:
        """play media from point.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is None:
            self._create_player()

        timestamp = helpers.seconds_to_time(seconds)
        self._player.start = timestamp

        self.play()

    def stop(self) -> None:
        """Stops the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            self._player.terminate()
            self._state = 0

    def pause(self) -> None:
        """Pauses the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            self._player.pause = True
            self._state = 2

    def seek(self, direction, amount) -> None:
        """Seek forward or backward in the media.

        Overrides method from Player; see documentation in that class.
        """
        assert direction == 1 or direction == -1
        if self._player is not None:
            self._player.seek(direction * amount)

    def set_rate(self, rate) -> None:
        """Set the playback speed.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            self._player.speed = rate

    def set_volume(self, volume) -> None:
        """Set the player volume.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            self._player.volume = volume

    @property
    def duration(self) -> int:
        """int: the duration of the player"""
        result = 0
        if self._player is not None:
            d = self._player.duration
            result = 5000 if d is None else d * constants.MILLISECONDS_IN_SECOND
        return result

    @property
    def volume(self) -> int:
        """int: the volume of the player"""
        if self._player is not None:
            return self._player.volume

    @property
    def time(self) -> int:
        """int: the current time of the player"""
        if self._player is not None:
            t = self._player.time_pos
            return 0 if t is None else t * constants.MILLISECONDS_IN_SECOND

    @property
    def time_str(self) -> str:
        """str: the formatted time and duration of the player"""
        result = "00:00:00/00:00:00"
        if self._player is not None:
            time_seconds = int(self.time / constants.MILLISECONDS_IN_SECOND)
            length_seconds = int(self.duration /
                    constants.MILLISECONDS_IN_SECOND)
            t = helpers.seconds_to_time(time_seconds)
            d = helpers.seconds_to_time(length_seconds)
            result = "%s/%s" % (t, d)
        return result
