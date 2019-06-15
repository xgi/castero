import curses

from castero.feed import Feed
from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu


class FeedMenu(Menu):
    """The menu for a podcast feed.
    """

    def __init__(self, window, source, child=None, active=False) -> None:
        assert child is not None and isinstance(child, EpisodeMenu)

        self._feeds = []

        super().__init__(window, source, child=child, active=active)

    def __len__(self) -> int:
        return len(self._feeds)

    @property
    def _items(self):
        """A list of items in the menu represented as dictionaries.

        Overrides method from Menu; see documentation in that class.
        """
        return [
            {
                'attr': curses.A_NORMAL,
                'tags': [],
                'text': str(feed)
            }
            for feed in self._feeds
        ]

    @property
    def item(self) -> Feed:
        """The selected feed.

        Overrides method from Menu; see documentation in that class.
        """
        if len(self._feeds) == 0:
            return None

        return self._feeds[self._selected]

    @property
    def metadata(self) -> str:
        """Metadata for the selected feed.

        Overrides method from Menu; see documentation in that class.
        """
        feed = self.item
        if feed is None:
            return ""

        return feed.metadata

    def update_items(self, obj):
        """Called by the parent menu (if we have one) to update our items.

        Overrides method from Menu; see documentation in that class.
        """
        super().update_items(obj)

        self._feeds = self._source.feeds()
        if self._inverted:
            self._feeds.reverse()

        self._sanitize()

    def update_child(self):
        """Update our child menu, the episode menu.

        Overrides method from Menu; see documentation in that class.
        """
        if len(self._feeds) == 0:
            self.update_items(None)
        else:
            self._child.update_items(self._feeds[self._selected])

    def invert(self):
        """Invert the menu order.

        Overrides method from Menu; see documentation in that class.
        """
        super().invert()

        self.update_items(None)
