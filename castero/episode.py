import os
import threading

from castero import constants
from castero import helpers
from castero.config import Config
from castero.datafile import DataFile


class Episode:
    """A single episode from a podcast feed.
    """

    PROGRESS_INDICATOR = "*"

    def __init__(self, feed, ep_id=None, title=None, description=None,
                 link=None, pubdate=None, copyright=None, enclosure=None,
                 played=False, progress=None) -> None:
        """
        At least one of a title or description must be specified.

        Args:
            feed: the feed that this episode is a part of
            title: (optional) the title of the episode
            description: (optional) the description of the episode
            link: (optional) a link to the episode
            pubdate: (optional) the date the episode was published, as a string
            copyright: (optional) the copyright notice of the episode
            enclosure: (optional) a url to a media file
            played: (optional) whether the episode has been played
        """
        assert title is not None or description is not None

        self._feed = feed
        self._ep_id = ep_id
        self._title = title
        self._description = description
        self._link = link
        self._pubdate = pubdate
        self._copyright = copyright
        self._enclosure = enclosure
        self._played = played
        self._progress = progress
        self._downloaded = None

    def __str__(self) -> str:
        """Represent this object as a single-line string.

        Returns:
            string: this episode's title, if it exists, else its description
        """
        if self._title is not None:
            representation = str(self._title)
        else:
            representation = str(self._description)

        representation = representation.split('\n')[0]

        return representation

    def _feed_directory(self) -> str:
        """Gets the path to the downloaded episode's feed directory.

        This method does not ensure whether the directory exists -- it simply
        acts as a single definition of where it _should_ be.

        Returns:
            str: a path to the feed directory
        """
        feed_dirname = helpers.sanitize_path(str(self._feed))
        if Config is None or Config["custom_download_dir"] == "":
            path = DataFile.DEFAULT_DOWNLOADED_DIR
        else:
            path = \
                os.path.expandvars(
                    os.path.expanduser(
                        Config["custom_download_dir"]))
            if not path.startswith('/'):
                path = "/%s" % path
        return os.path.join(path, feed_dirname)

    def get_playable(self) -> str:
        """Gets a playable path for this episode.

        This method checks whether the episode is available on the disk, giving
        the path to that file if so. Otherwise, simply return the episode's
        enclosure, which is probably a URL.

        Returns:
            str: a path to a playable file for this episode
        """
        playable = self.enclosure

        feed_directory = self._feed_directory()
        if os.path.exists(feed_directory):
            for File in os.listdir(feed_directory):
                if File.startswith(str(self.ep_id) + '-'):
                    playable = os.path.join(feed_directory, File)

        return playable

    def download(self, download_queue, display=None):
        """Downloads this episode to the file system.

        This method currently only supports downloading from an external URL.
        In the future, it may be worthwhile to determine whether the episode's
        source is a local file and simply copy it instead.

        Args:
            download_queue: the download_queue overseeing this download
            display: (optional) the display to write status updates to
        """
        if self._enclosure is None:
            if display is not None:
                display.change_status("Download failed: episode does not have"
                                      " a valid media source")
            return

        feed_directory = self._feed_directory()
        filename = "%s-%s%s" % (
            self.ep_id,
            helpers.sanitize_path(str(self)),
            str(os.path.splitext(self._enclosure)[1].split('?')[0])
        )
        output_path = os.path.join(feed_directory, filename)
        DataFile.ensure_path(output_path)

        if display is not None:
            display.change_status("Starting episode download...")

        t = threading.Thread(
            target=DataFile.download_to_file,
            args=[
                self._enclosure, output_path, str(self),
                download_queue, display
            ],
            name="download_%s" % str(self)
        )
        t.start()

    def delete(self, display=None):
        """Deletes the episode file from the file system.

        Args:
            display: (optional) the display to write status updates to
        """
        if self.downloaded:
            feed_directory = self._feed_directory()
            if os.path.exists(feed_directory):
                for File in os.listdir(feed_directory):
                    if File.startswith(str(self.ep_id) + '-'):
                        os.remove(os.path.join(feed_directory, File))
                        self._downloaded = False
                        if display is not None:
                            display.change_status(
                                "Successfully deleted the downloaded episode"
                            )

                # if there are no more files in the feed directory, delete it
                if len(os.listdir(feed_directory)) == 0:
                    os.rmdir(feed_directory)

    def check_downloaded(self) -> bool:
        """Check whether the episode is downloaded.

        This method updates the downloaded property.

        Returns:
            bool: whether or not the episode is downloaded
        """
        self._downloaded = False
        feed_directory = self._feed_directory()

        if os.path.exists(feed_directory):
            for File in os.listdir(feed_directory):
                if File.startswith(str(self.ep_id) + '-'):
                    self._downloaded = True
        return self._downloaded

    def replace_from(self, episode) -> None:
        """Replace metadata from the given episode.

        Args:
            episode: the source Episode
        """
        self._ep_id = episode._ep_id
        self._played = episode._played
        self._progress = episode._progress

    @property
    def downloaded(self) -> bool:
        """Determines whether the episode is downloaded.

        This method does not guarantee the episode exists, but it determines
        whether it "probably" does. If the download status has not been checked
        since the client started, we check it here and return the result.
        Some methods also update the download status. However, if a file is
        removed externally while the client is still running, the status may
        not be properly updated.

        Returns:
            bool: whether or not the episode is downloaded
        """
        if self._downloaded is None:
            self.check_downloaded()
        return self._downloaded

    @property
    def ep_id(self) -> int:
        """int: the database id of the episode"""
        return self._ep_id

    @ep_id.setter
    def ep_id(self, ep_id) -> None:
        self._ep_id = ep_id

    @property
    def feed_str(self) -> str:
        """str: the string representation of this episode's feed"""
        return str(self._feed)

    @property
    def title(self) -> str:
        """str: the title of the episode"""
        result = self._title
        if result is None:
            result = "Title not available."
        return result

    @property
    def description(self) -> str:
        """str: the description of the episode"""
        result = self._description
        if result is None:
            result = "Description not available."
        return result

    @property
    def link(self) -> str:
        """str: the link of/for the episode"""
        result = self._link
        if result is None:
            result = "Link not available."
        return result

    @property
    def pubdate(self) -> str:
        """str: the publish date of the episode"""
        result = self._pubdate
        if result is None:
            result = "Publish date not available."
        return result

    @property
    def copyright(self) -> str:
        """str: the copyright of the episode"""
        result = self._copyright
        if result is None:
            result = "No copyright specified."
        return result

    @property
    def enclosure(self) -> str:
        """str: the enclosure of the episode"""
        result = self._enclosure
        if result is None:
            result = "Enclosure not available."
        return result

    @property
    def played(self) -> bool:
        """bool: whether the episode has been played"""
        return self._played

    @played.setter
    def played(self, played) -> None:
        self._played = played

    @property
    def progress(self) -> int:
        """int: progress in milliseconds gathered from database"""
        progress = self._progress
        if progress is None:
            progress = 0
        return progress

    @progress.setter
    def progress(self, progress) -> None:
        self._progress = progress

    @property
    def metadata(self) -> str:
        """str: the user-displayed metadata of the episode"""
        description = helpers.html_to_plain(self.description) if \
            helpers.is_true(Config["clean_html_descriptions"]) else \
            self.description
        description = description.replace('\n', '')
        progress = helpers.seconds_to_time(self.progress / constants.MILLISECONDS_IN_SECOND)
        downloaded = "Episode downloaded and available for offline playback." \
            if self.downloaded else "Episode not downloaded."
        metadata = \
            "!cb{title}\n" \
            "{pubdate}\n\n" \
            "{link}\n\n" \
            "!cbCopyright:\n" \
            "{copyright}\n\n" \
            "!cbDownloaded:\n" \
            "{downloaded}\n\n" \
            "!cbDescription:\n" \
            "{description}\n\n" \
            "!cbTime Played:\n" \
            "{progress}\n".format(
                title=self.title,
                pubdate=self.pubdate,
                link=self.link,
                copyright=self.copyright,
                downloaded=downloaded,
                description=description,
                progress=progress)

        return metadata
