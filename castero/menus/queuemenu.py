from castero.feed import Feed
from castero.menu import Menu


class QueueMenu(Menu):
    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

        self._player_names = []

    def _items(self):
        return [str(player) for player in self._source]

    def update_items(self, obj):
        super().update_items(obj)

    def update_child(self):
        pass
