from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu

class FeedMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        assert child is not None and isinstance(child, EpisodeMenu)

        self._feeds = None

        super().__init__(window, source, child=child, active=active)

    def _items(self):
        return [str(feed) for feed in self._feeds]

    def update_items(self, obj):
        self._feeds = self._source.feeds()

    def update_child(self):
        if self._feeds is None:
            self.update_items(None)
        self._child.update_items(self._feeds[self._selected])