import curses

from castero import helpers
from castero.config import Config
from castero.menu import Menu
from castero.menus.queuemenu import QueueMenu
from castero.perspective import Perspective


class QueuePerspective(Perspective):
    """The queue-list perspective.

    This class handles display elements while in the queue perspective, which
    is a listing of the user's current Queue in which they can directly modify
    its state.
    """
    ID = 2

    def __init__(self, display) -> None:
        """
        Overrides method from Perspective; see documentation in that class.
        """
        super().__init__(display)
        self._active_window = 0
        self._queue_window = None
        self._metadata_window = None
        self._queue_menu = None
        self._metadata_updated = False

    def create_windows(self) -> None:
        """Create and set basic parameters for the windows.

        Overrides method from Perspective; see documentation in that class.
        """
        # delete old windows if they exist
        if self._queue_window is not None:
            del self._queue_window
            self._queue_window = None
        if self._metadata_window is not None:
            del self._metadata_window
            self._metadata_window = None

        parent_x = self._display.parent_x
        parent_y = self._display.parent_y
        third_x = helpers.third(parent_x)
        self._queue_window = curses.newwin(parent_y - 2, third_x * 2,
                                           2, 0)
        metadata_width = parent_x - ((third_x * 2) - 1)
        self._metadata_window = curses.newwin(parent_y - 3, metadata_width,
                                              2, 2 * third_x)

        # update menus if necessary
        if self._queue_menu is not None:
            self._queue_menu.window = self._queue_window

    def create_menus(self) -> None:
        """Create the menus used in each window.

        Overrides method from Perspective; see documentation in that class.
        """
        assert self._queue_window is not None

        self._queue_menu = QueueMenu(self._queue_window, self._display.queue,
                                     active=True)

    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.

        Overrides method from Perspective; see documentation in that class.
        """
        # clear dynamic menu headers
        self._queue_window.addstr(0, 0, " " * self._queue_window.getmaxyx()[1])

        # add window headers
        self._queue_window.addstr(0, 0, self._queue_menu.title,
                                  curses.color_pair(7) | curses.A_BOLD)
        self._metadata_window.addstr(0, 0, "Metadata",
                                     curses.color_pair(7) | curses.A_BOLD)

        # add window borders
        self._queue_window.hline(1, 0,
                                 0, self._queue_window.getmaxyx()[1],
                                 curses.ACS_HLINE | curses.color_pair(8))
        self._metadata_window.hline(1, 0,
                                    0, self._metadata_window.getmaxyx()[1] - 1,
                                    curses.ACS_HLINE | curses.color_pair(8))
        if not helpers.is_true(Config["disable_vertical_borders"]):
            self._queue_window.vline(0, self._queue_window.getmaxyx()[1] - 1,
                                     0, self._queue_window.getmaxyx()[0] - 2,
                                     curses.ACS_VLINE | curses.color_pair(8))

        # draw metadata
        if not self._metadata_updated:
            self._draw_metadata(self._metadata_window)
            self._metadata_window.refresh()
            self._metadata_updated = True

        self._queue_window.refresh()

    def display_all(self) -> None:
        """Force all windows to completely redraw their content.

        Overrides method from Perspective; see documentation in that class.
        """
        self._metadata_updated = False
        self._queue_menu.display()
        self.display()

    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Overrides method from Perspective; see documentation in that class.
        """
        queue = self._display.queue
        key_mapping = self._display.KEY_MAPPING

        keep_running = True
        if c == key_mapping[Config['key_play_selected']]:
            target = self._queue_menu.item
            self._display.queue.jump(target)
            while self._queue_menu.selected_index > 0:
                self._queue_menu.move(1)
            queue.play()
            self._display.menus_valid = False
        elif c == key_mapping[Config['key_next']]:
            queue.stop()
            queue.next()
            self._queue_menu.move(1)
            queue.play()
            self._display.menus_valid = False
        elif c == key_mapping[Config['key_clear']]:
            queue.stop()
            queue.clear()
            self._display.menus_valid = False
        elif c == key_mapping[Config['key_remove']]:
            self._remove_selected_from_queue()
        elif c == key_mapping[Config['key_show_url']]:
            item = self._queue_menu.item
            if item is not None:
                self._display.show_episode_url(item.episode)
        elif c == key_mapping[Config['key_execute']]:
            item = self._queue_menu.item
            if item is not None:
                self._display.execute_command(item.episode)
        elif c == key_mapping[Config['key_reload_selected']]:
            pass
        elif c == key_mapping[Config['key_save']]:
            pass
        elif c == key_mapping[Config['key_delete']]:
            pass
        elif c == key_mapping[Config['key_mark_played']]:
            pass
        elif c == key_mapping[Config['key_filter']]:
            pass
        else:
            keep_running = self._generic_handle_input(c)

        return keep_running

    def refresh(self) -> None:
        """Refresh the screen and all windows.

        Overrides method from Perspective; see documentation in that class.
        """
        self._queue_window.refresh()
        self._metadata_window.refresh()
        self._queue_menu.refresh()

    def made_active(self) -> None:
        """Called each time the perspective is made active (switched to).

        Overrides method from Perspective; see documentation in that class.
        """
        pass

    def update_menus(self) -> None:
        """Update/refresh the contents of all menus.

        Overrides method from Perspective; see documentation in that class.
        """
        self._queue_menu.update_items(None)
        self._metadata_updated = False

    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Overrides method from Perspective; see documentation in that class.
        """
        assert 0 <= self._active_window < 2

        return self._queue_menu

    def _invert_selected_menu(self) -> None:
        """Inverts the contents of the selected menu.

        Overrides method from Perspective; see documentation in that class.
        """
        pass

    def _remove_selected_from_queue(self) -> None:
        """Remove the selected player from the queue.
        """
        player = self._queue_menu.item
        if player is not None:
            index = self._display.queue.remove(player)
            self._queue_menu.update_items(None)
            for i in range(index):
                self._get_active_menu().move(-1)
        self._metadata_updated = False
