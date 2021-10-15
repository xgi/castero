import curses
import threading
import os

from castero.config import Config
from castero.datafile import DataFile
from castero.episode import Episode
from castero.menu import Menu


class DownloadedMenu(Menu):
    """The menu for episodes in a feed."""

    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._episodes = []

    def __len__(self) -> int:
        return len(self._filtered_episodes)

    @property
    def _items(self):
        """A list of items in the menu represented as dictionaries."""
        result = []
        for episode in self._filtered_episodes:
            result.append(
                {
                    "attr": curses.color_pair(5) if episode.played else curses.A_NORMAL,
                    "tags": [],
                    "text": "[%s] %s" % (episode.feed_str, str(episode)),
                }
            )
        return result

    @property
    def title(self) -> str:
        """The title of the menu to display in the window header."""
        base = "Downloaded Episodes"
        if len(self._filtered_episodes) > 0:
            unplayed_episodes = 0
            for episode in self._filtered_episodes:
                if not episode.played:
                    unplayed_episodes += 1

            return "%s (%d/%d)" % (base, unplayed_episodes, len(self._filtered_episodes))
        return base

    @property
    def item(self) -> Episode:
        """The selected episode."""
        if len(self._filtered_episodes) == 0:
            return None

        return self._filtered_episodes[self._selected]

    @property
    def metadata(self) -> str:
        """Metadata for the selected episode."""
        if len(self._filtered_episodes) == 0:
            return ""

        return self._filtered_episodes[self._selected].metadata

    def update_items(self, obj):
        """Called by the parent menu (if we have one) to update our items."""
        super().update_items(obj)

        t = threading.Thread(target=self._find_downloaded_episodes, name="find_downloaded_episodes")
        t.start()

        self._sanitize()

    def _find_downloaded_episodes(self):
        if Config is None or Config["custom_download_dir"] == "":
            path = DataFile.DEFAULT_DOWNLOADED_DIR
        else:
            path = os.path.expandvars(os.path.expanduser(Config["custom_download_dir"]))
            if not path.startswith("/"):
                path = "/%s" % path

        self._episodes = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                ep_id = filename.split("-")[0]
                if ep_id.isdigit():
                    episode = self._source.episode(int(ep_id))
                    if episode is not None:
                        self._episodes.append(episode)

        if self._inverted:
            self._episodes.reverse()
        self._sanitize()
        self.display()

    def update_child(self):
        """Not necessary for this menu -- does nothing."""
        pass

    def invert(self):
        """Invert the menu order."""
        super().invert()

        self.update_items(None)

    @property
    def _filtered_episodes(self):
        """A list of episodes which match the menu filter."""
        return list(filter(lambda ep: self._filter_text in str(ep).lower(), self._episodes))
