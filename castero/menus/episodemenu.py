import curses

from castero import helpers
from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed
from castero.menu import Menu


class EpisodeMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._feed = None
        self._episode_dicts = []

    def __len__(self) -> int:
        return len(self._episode_dicts)

    def _items(self):
        return [
            {
                'attr': curses.color_pair(5) if tpl['played'] else curses.A_NORMAL,
                'text': tpl['text']
            }
            for tpl in self._episode_dicts
        ]

    def item(self) -> Episode:
        if len(self._episode_dicts) == 0:
            return None

        tpl = self._episode_dicts[self._selected]
        return self._source.episode(tpl['ep_id'])

    def metadata(self):
        if len(self._episode_dicts) == 0:
            return ""

        tpl = self._episode_dicts[self._selected]
        if tpl is None:
            return ""

        return tpl['metadata']

    def update_items(self, feed: Feed):
        assert isinstance(feed, Feed) or feed is None

        super().update_items(feed)

        self._feed = feed

        if feed is None:
            self._episode_dicts = []
        else:
            self._episode_dicts = [
                {
                    'ep_id': episode.ep_id,
                    'text': str(episode),
                    'played': episode.played,
                    'metadata': episode.metadata
                }
                for episode in self._source.episodes(feed)
            ]

            if self._inverted:
                self._episode_dicts.reverse()

        self._sanitize()

    def update_child(self):
        pass

    def invert(self):
        super().invert()

        self.update_items(self._feed)
