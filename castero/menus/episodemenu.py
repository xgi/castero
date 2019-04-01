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
        self._episodes = []

    def __len__(self) -> int:
        return len(self._episodes)

    def _items(self):
        result = []
        for episode in self._episodes:
            tags = []
            if episode.downloaded:
                tags.append('D')

            result.append({
                'attr': curses.color_pair(5) if episode.played else curses.A_NORMAL,
                'tags': tags,
                'text': str(episode)
            })
        return result

    def item(self) -> Episode:
        if len(self._episodes) == 0:
            return None

        return self._episodes[self._selected]

    def metadata(self):
        if len(self._episodes) == 0:
            return ""

        return self._episodes[self._selected].metadata

    def update_items(self, feed: Feed):
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
        pass

    def invert(self):
        super().invert()

        self.update_items(self._feed)
