import os
from castero import helpers
from castero.datafile import DataFile


class Episode:
    """The Episode class.

    This class represents a single episode from a podcast feed.
    """
    def __init__(self, title=None, description=None, link=None,
                 pubdate=None, copyright=None, enclosure=None) -> None:
        """Initializes the object.

        At least one of a title or description must be specified.

        Args:
            title: (optional) the title of the episode
            description: (optional) the description of the episode
            link: (optional) a link to the episode
            pubdate: (optional) the date the episode was published, as a string
            copyright: (optional) the copyright notice of the episode
            enclosure: (optional) a url to a media file
        """
        assert title is not None or description is not None

        self._title = title
        self._description = description
        self._link = link
        self._pubdate = pubdate
        self._copyright = copyright
        self._enclosure = enclosure

    def __str__(self) -> str:
        """Represent this object as a single-line string.

        Returns:
            string: this episode's title, if it exists, else its description
        """
        if self._title is not None:
            representation = self._title
        else:
            representation = self._description
        return representation.split('\n')[0]

    def get_playable(self, feed) -> str:
        """Gets a playable path for this episode.

        This method checks whether the episode is available on the disk, giving
        the path to that file if so. Otherwise, simply return the episode's
        enclosure, which is probably a URL.

        Args:
            feed: the castero.Feed that this episode is from

        Returns:
            str: a path to a playable file for this episode
        """
        playable = self.enclosure

        feed_dirname = helpers.sanitize_path(str(feed))
        episode_partial_filename = helpers.sanitize_path(str(self))
        feed_directory = os.path.join(DataFile.DOWNLOADED_DIR, feed_dirname)

        if os.path.exists(feed_directory):
            for File in os.listdir(feed_directory):
                if File.startswith(episode_partial_filename + '.'):
                    playable = os.path.join(feed_directory, File)

        return playable

    @property
    def title(self) -> str:
        result = self._title
        if result is None:
            result = "Title not available."
        return result

    @property
    def description(self) -> str:
        result = self._description
        if result is None:
            result = "Description not available."
        return result

    @property
    def link(self) -> str:
        result = self._link
        if result is None:
            result = "Link not available."
        return result

    @property
    def pubdate(self) -> str:
        result = self._pubdate
        if result is None:
            result = "Publish date not available."
        return result

    @property
    def copyright(self) -> str:
        result = self._copyright
        if result is None:
            result = "Copyright not available."
        return result

    @property
    def enclosure(self) -> str:
        result = self._enclosure
        if result is None:
            result = "Enclosure not available."
        return result
