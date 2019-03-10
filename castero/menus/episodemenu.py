from castero.feed import Feed
from castero.menu import Menu


class EpisodeMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._parent_feed = None

    def _items(self):
        return [str(episode) for episode in
                self._source.episodes(self._parent_feed)]

    def update_items(self, feed: Feed):
        assert isinstance(feed, Feed)

        self._parent_feed = feed

    def update_child(self):
        pass
