import curses
from abc import ABC, abstractmethod, abstractproperty
from typing import List


class Menu(ABC):
    """The Menu class.

    This class is used to display interactable menus. It displays a list of
    items to its window and allows the user to cycle through them.

    This class does not handle user input -- that is done in the Display class.
    Methods in that class simply call appropriate methods here in response to
    user input in order to change the state of the menu.
    """

    @abstractmethod
    def __init__(self, window, source, child=None, active=False) -> None:
        """Initializes the object.

        Args:
            window: the curses.window which this menu is placed on
            items: a 2D array where rows represent indices of the parent menu
            child: (optional, default None) the submenu of this menu
            active: (optional, default False) whether this menu is active
        """
        assert window.getmaxyx()[0] >= 3
        assert child is None or isinstance(child, Menu)
        assert isinstance(active, bool)

        self._window = window
        self._source = source
        self._child = child
        self._active = active
        self._selected = 0
        self._display_start_y = 2
        self._top_index = 0
        self._max_displayed_items = self._window.getmaxyx()[0] - 4
        self._inverted = False

        if child is not None:
            self.update_child()

    @abstractmethod
    def __len__(self) -> int:
        """int: the number of items in the menu"""

    @abstractproperty
    @property
    def _items(self) -> List[str]:
        """List[str]: the current items in this menu"""

    @abstractproperty
    @property
    def item(self):
        """the selected item"""

    @abstractproperty
    @property
    def metadata(self) -> str:
        """str: metadata for the selected item"""

    @abstractmethod
    def update_items(self, obj) -> None:
        """Called by the parent menu (if we have one) to update our items.

        Args:
            obj: an object of some type understood by the specific
            implementation of this menu
        """

    @abstractmethod
    def update_child(self) -> None:
        """Implementation-specific method to update our child, if we have one.

        This method calls the child's update_items with an
        implementation-specific object understood by the child.
        """

    @abstractmethod
    def invert(self) -> None:
        """Invert the menu order.

        Inversion is not just a visual effect -- the contents of the items list
        must also be reversed.
        """
        self._inverted = not self._inverted

    def _pad_text(self, text) -> str:
        """Pads an item string with spaces to be the full length of the menu.

        Note that this does not create a string the entire length of the
        window, it only makes it as large as the menu. Since the window has a
        border, the string will be 1 column shorter than the window.

        Args:
            item: the item text as a string

        Returns:
            str: a string the length of the menu, with the left justified item
        """
        max_width = self._window.getmaxyx()[1] - 1
        return text.ljust(max_width)[:max_width]

    def _draw_item(self, index, position) -> None:
        """Draws an item's text on the window.

        This method applies the appropriate color pair to the item: 2 if the
        item is selected and the window is active, 3 if the item is selected
        but the window is not active, and 1 otherwise.

        Args:
            index: the index of the item
            position: the y-position to draw the item, without accounting
                for _display_start_y
        """
        item = self._items()[index]
        
        tag_str = ""
        if len(item['tags']) > 0:
            tag_str = "".join(["[%s]" % tag for tag in item['tags']]) + " "

        text = tag_str + item['text']

        attr = curses.color_pair(1)
        if index == self._selected:
            if self._active:
                attr = curses.color_pair(2)
            else:
                attr = curses.color_pair(3)
        else:
            attr = attr | item['attr']

        self._window.addstr(self._display_start_y + position, 0,
                            self._pad_text(text), attr)

    def _sanitize(self) -> None:
        """Sanitizes _selected and _top_index.

        Checks that _selected and _top_index are valid (inside all boundaries),
        setting them to appropriate extremes if they are not.
        """
        num_my_items = len(self)

        # _selected cannot be outside range of items
        if self._selected < 0:
            self._selected = 0
        if self._selected > num_my_items - 1:
            self._selected = num_my_items - 1

        # if there is no next page, then the current page should be as full
        # as possible
        if self._top_index + self._max_displayed_items > num_my_items:
            self._top_index = num_my_items - self._max_displayed_items

        # _top_index cannot be outside range of items
        if self._top_index > num_my_items - 1:
            self._top_index = num_my_items - 1
        if self._top_index < 0:
            self._top_index = 0

    def display(self) -> None:
        """Draw all visible items on this menu to the window.

        Visible items are items with an index greater than or equal to
        _top_index but less than _max_displayed_items greater than _top_index.
        That is, all items that can fit on the screen starting from _top_index.
        """
        position = 0
        for i in range(self._top_index,
                       self._top_index + self._max_displayed_items):
            if i <= len(self) - 1:
                self._draw_item(i, position)
                position += 1

        # fill unused rows with blank lines
        for y in range(self._display_start_y + position,
                       self._display_start_y + self._max_displayed_items):
            self._window.addstr(y, 0, self._pad_text(""))

    def set_active(self, active) -> None:
        """Sets whether this menu is active.

        The only effect this method has on this object is whether or not to
        display the selected item as yellow or as grayed-out. Any movement
        operations could still be run, but doing so would confuse the user
        assuming _active has been properly set.

        Args:
            active: whether this menu is active or not
        """
        assert isinstance(active, bool)

        self._active = active

    def move(self, direction) -> None:
        """Change the selected item to an adjacent item.

        Args:
            direction: 1 to move up, -1 to move down
        """
        assert direction == 1 or direction == -1

        self._selected -= direction

        if self._selected < self._top_index:
            # the cursor went above the menu
            self._top_index -= 1
        elif self._selected >= self._top_index + self._max_displayed_items:
            # the cursor went below the menu
            self._top_index += 1

        self._sanitize()
        if self._child is not None:
            self.update_child()

    def move_page(self, direction) -> None:
        """Change the selected item to the next "page".

        Effectively the same as moving _max_displayed_items times.

        We always try to make the menu as full as possible -- if the movement
        would leave us with only a few items on the screen, we instead reset
        _top_index to make the screen as full as possible. Therefore we can
        assume that if there are enough items in the menu to fill the screen,
        the menu will *always* fill the screen.

        Args:
            direction: 1 to move up, -1 to move down
        """
        assert direction == 1 or direction == -1

        if direction == 1:
            self._selected -= self._max_displayed_items
            self._top_index -= self._max_displayed_items
        elif direction == -1:
            self._selected += self._max_displayed_items
            self._top_index += self._max_displayed_items

        self._sanitize()
        if self._child is not None:
            self.update_child()

    @property
    def selected_index(self) -> int:
        """int: the current selected index of the menu"""
        return self._selected

    @property
    def window(self):
        """window: the curses.window which this menu is placed on"""
        return self._window

    @window.setter
    def window(self, window) -> None:
        self._window = window