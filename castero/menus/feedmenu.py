from castero import helpers
from castero.config import Config
from castero.feed import Feed
from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu


class FeedMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        assert child is not None and isinstance(child, EpisodeMenu)

        self._feeds = None

        super().__init__(window, source, child=child, active=active)

    def _items(self):
        return [str(feed) for feed in self._feeds]

    def item(self) -> Feed:
        if len(self._feeds) == 0:
            return None
        
        return self._feeds[self._selected]

    def metadata(self):
        feed = self.item()
        if feed is None:
            return ""

        description = helpers.html_to_plain(feed.description) if \
            helpers.is_true(Config["clean_html_descriptions"]) else \
            feed.description

        return \
            f"\cb{feed.title}\n" \
            f"{feed.last_build_date}\n\n" \
            f"{feed.link}\n\n" \
            f"\cbDescription:\n" \
            f"{description}\n\n" \
            f"\cbCopyright:\n" \
            f"{feed.copyright}\n"

    def update_items(self, obj):
        super().update_items(obj)

        self._feeds = self._source.feeds()

    def update_child(self):
        if self._feeds is None:
            self.update_items(None)
        self._child.update_items(self._feeds[self._selected])
