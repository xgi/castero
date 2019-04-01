import curses

from castero import helpers
from castero.config import Config
from castero.feed import Feed
from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu


class FeedMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        assert child is not None and isinstance(child, EpisodeMenu)

        self._feeds = []

        super().__init__(window, source, child=child, active=active)

    def __len__(self) -> int:
        return len(self._feeds)

    def _items(self):
        return [
            {
                'attr': curses.A_NORMAL,
                'tags': [],
                'text': str(feed)
            }
            for feed in self._feeds
        ]

    def item(self) -> Feed:
        if len(self._feeds) == 0:
            return None
        
        return self._feeds[self._selected]

    def metadata(self):
        feed = self.item()
        if feed is None:
            return ""

        return feed.metadata

    def update_items(self, obj):
        super().update_items(obj)

        self._feeds = self._source.feeds()
        if self._inverted:
            self._feeds.reverse()

        self._sanitize()

    def update_child(self):
        if len(self._feeds) == 0:
            self.update_items(None)
        else:
            self._child.update_items(self._feeds[self._selected])

    def invert(self):
        super().invert()

        self.update_items(None)
