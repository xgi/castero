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
        return [pair[1] for pair in self._episode_tuples]

    def item(self) -> Episode:
        if len(self._episode_tuples) == 0:
            return None
        
        pair = self._episode_tuples[self._selected]
        return self._source.episode(pair[0])

    def metadata(self):
        episode = self.item()
        if episode is None:
            return ""

        description = helpers.html_to_plain(episode.description) if \
            helpers.is_true(Config["clean_html_descriptions"]) else \
            episode.description
        downloaded = "Episode downloaded and available for offline playback." \
            if episode.downloaded() else "Episode not downloaded."

        return \
            f"\cb{episode.title}\n" \
            f"{episode.pubdate}\n\n" \
            f"{episode.link}\n\n" \
            f"\cbDescription:\n" \
            f"{description}\n\n" \
            f"\cbCopyright:\n" \
            f"{episode.copyright}\n\n" \
            f"\cbDownloaded:\n" \
            f"{downloaded}\n"

    def update_items(self, feed: Feed):
        assert isinstance(feed, Feed)

        super().update_items(feed)

        self._feed = feed

        self._episode_tuples = \
            [(pair[0], str(pair[1])) for pair in self._source.episodes(feed)]
        if self._inverted:
            self._episode_tuples.reverse()

    def update_child(self):
        pass

    def invert(self):
        super().invert()

        self.update_items(self._feed)