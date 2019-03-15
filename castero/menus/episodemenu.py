from castero import helpers
from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed
from castero.menu import Menu


class EpisodeMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._feed = None
        self._episode_tuples = []  # episodes in the form (id, title)

    def __len__(self) -> int:
        return len(self._episode_tuples)

    def _items(self):
        return [tpl[1] for tpl in self._episode_tuples]

    def item(self) -> Episode:
        if len(self._episode_tuples) == 0:
            return None
        
        tpl = self._episode_tuples[self._selected]
        return self._source.episode(tpl[0])

    def metadata(self):
        if len(self._episode_tuples) == 0:
            return ""

        tpl = self._episode_tuples[self._selected]
        if tpl is None:
            return ""
        
        return tpl[2]

    def update_items(self, feed: Feed):
        assert isinstance(feed, Feed) or feed is None

        super().update_items(feed)

        self._feed = feed

        if feed is None:
            self._episode_tuples = []
        else:
            self._episode_tuples = \
                [(episode.ep_id, str(episode), episode.metadata) for episode in self._source.episodes(feed)]
            if self._inverted:
                self._episode_tuples.reverse()

    def update_child(self):
        pass

    def invert(self):
        super().invert()

        self.update_items(self._feed)