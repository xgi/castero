from castero.feed import Feed
from castero.menu import Menu


class EpisodeMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._episode_names = []

    def _items(self):
        return self._episode_names

    def update_items(self, feed: Feed):
        assert isinstance(feed, Feed)

        super().update_items(feed)

        self._episode_names = [str(episode) for episode in \
            self._source.episodes(feed)]

    def update_child(self):
        pass
