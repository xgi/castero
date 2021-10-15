import curses
import threading

from castero.episode import Episode
from castero.feed import Feed
from castero.menu import Menu
from castero import helpers


class EpisodeMenu(Menu):
    """The menu for episodes in a feed."""

    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._feed = None
        self._episodes = []

    def __len__(self) -> int:
        return len(self._filtered_episodes)

    @property
    def _items(self):
        """A list of items in the menu represented as dictionaries."""
        result = []
        for episode in self._filtered_episodes:
            tags = []
            if episode.downloaded:
                tags.append("D")
            if episode.progress > 0:
                tags.append(Episode.PROGRESS_INDICATOR)

            result.append(
                {
                    "attr": curses.color_pair(5) if episode.played else curses.A_NORMAL,
                    "tags": tags,
                    "text": str(episode),
                }
            )
        return result

    @property
    def title(self) -> str:
        """The title of the menu to display in the window header."""
        base = "Episodes"
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

    def update_items(self, feed):
        """Called by the parent menu (the feeds menu) to update our items."""
        assert isinstance(feed, Feed) or feed is None

        super().update_items(feed)

        self._feed = feed

        if feed is None:
            self._episodes = []
        else:
            t = threading.Thread(
                target=self._request_source_episodes, args=[feed], name="episodes_%s" % feed
            )
            t.start()

        self._sanitize()

    def _request_source_episodes(self, feed):
        episodes = self._source.episodes(feed)

        # the above may have taken some time; ensure the user hasn't
        # selected another feed
        if self._feed == feed:
            self._episodes = sorted(
                episodes, reverse=not self._inverted, key=lambda ep: helpers.datetime_from_rfc822(ep.pubdate)
            )

            self._sanitize()
            self.display()

    def update_child(self):
        """Not necessary for this menu -- does nothing."""
        pass

    def invert(self):
        """Invert the menu order."""
        super().invert()

        self.update_items(self._feed)

    @property
    def _filtered_episodes(self):
        """A list of episodes which match the menu filter."""
        return list(filter(lambda ep: self._filter_text in str(ep).lower(), self._episodes))
