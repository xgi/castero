import time

from castero.player import Player, PlayerDependencyError


class VLCPlayer(Player):
    """The VLCPlayer class.
    """
    NAME = "vlc"

    def __init__(self, title, path, episode) -> None:
        """Initializes the object.

        Overrides method from Player; see documentation in that class.
        """
        super().__init__(title, path, episode)

        import vlc
        self.vlc = vlc

    @staticmethod
    def check_dependencies():
        """Checks whether dependencies are met for playing a player.

        Overrides method from Player; see documentation in that class.
        """
        try:
            import vlc
            i = vlc.Instance()
            vlc.libvlc_release(i)
        except (ImportError, NameError, OSError, AttributeError):
            raise PlayerDependencyError(
                "Dependency VLC not found, which is required for playing"
                " media files"
            )

    def _create_player(self) -> None:
        """Creates the player object while making sure it is a valid file.

        Overrides method from Player; see documentation in that class.
        """
        vlc_instance = self.vlc.Instance("--no-video --quiet")

        self._player = vlc_instance.media_player_new()
        self._media = vlc_instance.media_new(self._path)
        self._media.parse()  # may output some junk into the console
        self._player.set_media(self._media)

        self._duration = self._media.get_duration()

    def play(self) -> None:
        """Plays the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is None:
            self._create_player()

        self._player.play()
        self._state = 1

    def stop(self) -> None:
        """Stops the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            if self._player.get_state() == self.vlc.State.Opening:
                self._player.release()
            else:
                self._player.stop()
                self._state = 0

    def pause(self) -> None:
        """Pauses the media.

        Overrides method from Player; see documentation in that class.
        """
        if self._player is not None:
            if self._player.get_state() != self.vlc.State.Opening:
                self._player.pause()
                self._state = 2

    def seek(self, direction, amount) -> None:
        """Seek forward or backward in the media.

        Overrides method from Player; see documentation in that class.
        """
        assert direction == 1 or direction == -1
        if self._player is not None:
            self._player.set_time(
                self._player.get_time() + (direction * amount * 1000)
            )

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
