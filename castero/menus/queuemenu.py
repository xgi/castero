from castero import helpers
from castero.config import Config
from castero.feed import Feed
from castero.menu import Menu


class QueueMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

    def __len__(self) -> int:
        return self._source.length

    def _items(self):
        return [str(player) for player in self._source]

    def item(self) -> Feed:
        if self._source.length == 0:
            return None
        
        return self._source[self._selected]

    def metadata(self):
        player = self.item()
        if player is None:
            return ""
        episode = player.episode

        description = helpers.html_to_plain(episode.description) if \
            helpers.is_true(Config["clean_html_descriptions"]) else \
            episode.description
        description = description.replace('\n', '')
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

    def update_items(self, obj):
        super().update_items(obj)

    def update_child(self):
        pass

    def invert(self):
        pass
