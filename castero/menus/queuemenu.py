import curses

from castero.player import Player
from castero.menu import Menu


class QueueMenu(Menu):
    """The menu for the player queue.
    """

    def __init__(self, window, source, child=None, active=False) -> None:
        super().__init__(window, source, child=child, active=active)

    def __len__(self) -> int:
        return self._source.length

    @property
    def _items(self):
        """A list of items in the menu represented as dictionaries.

        Overrides method from Menu; see documentation in that class.
        """
        return [
            {
                'attr': curses.A_NORMAL,
                'tags': [],
                'text': str(player)
            }
            for player in self._source
        ]

    @property
    def title(self) -> str:
        """The title of the menu to display in the window header.

        Overrides method from Menu; see documentation in that class."""
        return "Queue"

    @property
    def item(self) -> Player:
        """The selected player.

        Overrides method from Menu; see documentation in that class.
        """
        if self._source.length == 0:
            return None

        return self._source[self._selected]

    @property
    def metadata(self) -> str:
        """Metadata for the selected player's episode.

        Overrides method from Menu; see documentation in that class.
        """
        player = self.item
        if player is None:
            return ""

        return player.episode.metadata

    def update_items(self, obj):
        """Called by the parent menu (if we have one) to update our items.

        Overrides method from Menu; see documentation in that class.
        """
        super().update_items(obj)
        self.display()

    def update_child(self):
        """Not necessary for this menu -- does nothing.

        Overrides method from Menu; see documentation in that class.
        """
        pass

    def invert(self):
        """Invert the menu order.

        Overrides method from Menu; see documentation in that class.
        """
        pass
