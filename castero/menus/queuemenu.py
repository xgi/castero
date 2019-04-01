import curses

from castero import helpers
from castero.config import Config
from castero.player import Player
from castero.menu import Menu


class QueueMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

    def __len__(self) -> int:
        return self._source.length

    def _items(self):
        return [
            {
                'attr': curses.A_NORMAL,
                'tags': [],
                'text': str(player)
            }
            for player in self._source
        ]

    def item(self) -> Player:
        if self._source.length == 0:
            return None
        
        return self._source[self._selected]

    def metadata(self):
        player = self.item()
        if player is None:
            return ""

        return player.episode.metadata

    def update_items(self, obj):
        super().update_items(obj)

    def update_child(self):
        pass

    def invert(self):
        pass
