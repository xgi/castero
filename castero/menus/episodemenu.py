import curses

from castero.episode import Episode
from castero.feed import Feed
from castero.menu import Menu


class EpisodeMenu(Menu):
    """The menu for episodes in a feed.
    """

    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._feed = None
        self._episodes = []

    def __len__(self) -> int:
        return len(self._episodes)

    @property
    def _items(self):
        """A list of items in the menu represented as dictionaries.

        Overrides method from Menu; see documentation in that class.
        """
        result = []
        for episode in self._episodes:
            tags = []
            if episode.downloaded:
                tags.append('D')

            result.append({
                'attr': curses.color_pair(5) if episode.played else
                curses.A_NORMAL,
                'tags': tags,
                'text': str(episode)
            })
        return result

    @property
    def item(self) -> Episode:
        """The selected episode.

        Overrides method from Menu; see documentation in that class.
        """
        if len(self._episodes) == 0:
            return None

        return self._episodes[self._selected]

    @property
    def metadata(self) -> str:
        """Metadata for the selected episode.

        Overrides method from Menu; see documentation in that class.
        """
        if len(self._episodes) == 0:
            return ""

        return self._episodes[self._selected].metadata

    def update_items(self, feed: Feed):
        """Called by the parent menu (the feeds menu) to update our items.

        Overrides method from Menu; see documentation in that class.
        """
        assert isinstance(feed, Feed) or feed is None

        super().update_items(feed)

        self._feed = feed

        if feed is None:
            self._episodes = []
        else:
            self._episodes = \
                [episode for episode in self._source.episodes(feed)]

            if self._inverted:
                self._episodes.reverse()

        self._sanitize()

    def update_child(self):
        """Not necessary for this menu -- does nothing.

        Overrides method from Menu; see documentation in that class.
        """
        pass

    def invert(self):
        """Invert the menu order.

        Overrides method from Menu; see documentation in that class.
        """
        super().invert()

        self.update_items(self._feed)
