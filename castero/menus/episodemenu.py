from castero import helpers
from castero.config import Config
from castero.feed import Feed
from castero.menu import Menu


class EpisodeMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._feed = None
        self._episode_tuples = []  # episodes in the form (id, title)

    def _items(self):
        return [pair[1] for pair in self._episode_tuples]

    def metadata(self):
        if len(self._episode_tuples) == 0:
            return ""

        pair = self._episode_tuples[self._selected]
        episode = self._source.episode(pair[0])

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

    def update_child(self):
        pass