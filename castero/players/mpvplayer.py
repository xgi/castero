import time

import castero
from castero.player import Player, PlayerDependencyError


class MPVPlayer(Player):
    """The MPVPlayer class.
    """
    NAME = "mpv"

    def __init__(self, title, path, episode) -> None:
        """Initializes the object.

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
        except (OSError, ModuleNotFoundError):
            raise PlayerDependencyError(
                "Dependency mpv not found, which is required for playing"
                " media files. If you recently downloaded it, you may need to"
                " reinstall %s" % castero.__title__
            )

    def _create_player(self) -> None:
        """Creates the player object while making sure it is a valid file.

        Overrides method from Player; see documentation in that class.
        """
        self._player = self.mpv.Context()
        self._player.initialize()
        self._player.set_option('vid', False)
        self._player.set_property('pause', True)

        self._player.command('loadfile', self._path)

        self._duration = self._player.time

    def play(self) -> None:
        """Plays the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is None:
            self._create_player()

        self._player.set_property('pause', False)
        self._state = 1

    def stop(self) -> None:
        """Stops the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            self._player.shutdown()
            self._state = 0

    def pause(self) -> None:
        """Pauses the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            self._player.set_property('pause', True)
            self._state = 2

    def seek(self, direction, amount) -> None:
        """Seek forward or backward in the media.

        Overrides method from Player; see documentation in that class.
        """
        assert direction == 1 or direction == -1
        if self._player is not None:
            self._player.command('seek', direction * amount)

    @property
    def duration(self) -> int:
        """int: the duration of the player"""
        try:
            return self._player.get_property('duration') * 1000
        except self.mpv.MPVError:
            return 5000

    @property
    def time(self) -> int:
        """int: the current time of the player"""
        if self._player is not None:
            try:
                return self._player.get_property('playback-time') * 1000
            except self.mpv.MPVError:
                return 0

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
