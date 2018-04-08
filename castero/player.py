import vlc
import time


class PlayerError(Exception):
    """An ambiguous error while handling the player.
    """


class PlayerCreateError(PlayerError):
    """An error occurred while creating the player.
    """


class Player:
    """The Player class.
    """
    SEEK_DISTANCE = 30 * 1000  # 10 seconds

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
        self._mrl = None  # media resource locator
        self._duration = -1  # in milliseconds
        self._state = 0  # 0=stopped, 1=playing, 2=paused

        self._create_player()

    def __del__(self) -> None:
        if self._player is not None:
            self.stop()

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

        if self._media.get_parsed_status == vlc.MediaParsedStatus.failed:
            raise PlayerCreateError(
                "Media object failed while parsing (is the path valid?)")

        self._duration = self._media.get_duration()

    def play(self) -> None:
        """Plays the media.

        If the media is an external stream, we may not have gotten metadata
        about the media when it was created. However, it should become
        accessible once the stream has begun playing, since VLC downloads the
        stream. Therefore, we try to retrieve this metadata here.
        """
        assert self._player is not None

        self._player.play()
        self._state = 1

    def stop(self) -> None:
        """Stops the media.
        """
        assert self._player is not None

        self._player.stop()
        self._state = 0

    def pause(self) -> None:
        """Pauses the media.
        """
        assert self._player is not None

        self._player.pause()
        self._state = 2

    def seek(self, direction, amount) -> None:
        """Seek forward or backward in the media.

        Args:
            direction: 1 to seek forward, -1 to seek backward
            amount: the amount of seconds to seek
        """
        assert direction == 1 or direction == -1
        assert self._player is not None

        self._player.set_time(
            self._player.get_time() + (direction * amount * 1000)
        )

    @property
    def state(self) -> int:
        return self._state

    @property
    def title(self) -> str:
        return self._title

    @property
    def duration(self) -> int:
        assert self._media is not None

        self._duration = self._media.get_duration()
        return self._duration

    @property
    def time(self) -> int:
        assert self._player is not None

        return self._player.get_time()

    @property
    def time_str(self):
        assert self._player is not None

        time_seconds = int(self.time / 1000)
        length_seconds = int(self.duration / 1000)
        t = time.strftime('%H:%M:%S', time.gmtime(time_seconds))
        d = time.strftime('%H:%M:%S', time.gmtime(length_seconds))

        return "%s/%s" % (t, d)
