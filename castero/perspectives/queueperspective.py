import curses

from castero import helpers
from castero.config import Config
from castero.menu import Menu
from castero.menus.queuemenu import QueueMenu
from castero.perspective import Perspective


class QueuePerspective(Perspective):
    """The QueuePerspective class.

    This class handles display elements while in the queue perspective, which
    is a listing of the user's current Queue in which they can directly modify
    its state.
    """
    ID = 2

    def __init__(self, display) -> None:
        """Initializes the object.

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
        self._metadata_window = curses.newwin(parent_y - 2, metadata_width,
                                              2, 2 * third_x)

        self._queue_window.attron(curses.color_pair(1))
        self._metadata_window.attron(curses.color_pair(1))

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
        # add window titles
        self._queue_window.attron(curses.A_BOLD)
        self._metadata_window.attron(curses.A_BOLD)
        self._queue_window.addstr(0, 0, "Queue")
        self._metadata_window.addstr(0, 0, "Metadata")

        # add window borders
        self._queue_window.hline(1, 0,
                                 0, self._queue_window.getmaxyx()[1])
        self._metadata_window.hline(1, 0,
                                    0, self._metadata_window.getmaxyx()[1] - 1)
        if not helpers.is_true(Config["disable_vertical_borders"]):
            self._queue_window.vline(0, self._queue_window.getmaxyx()[1] - 1,
                                     0, self._queue_window.getmaxyx()[0] - 2)

        # display menu content
        self._queue_menu.display()

        # draw metadata
        if not self._metadata_updated:
            self._draw_metadata(self._metadata_window)

    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Overrides method from Perspective; see documentation in that class.
        """
        queue = self._display.queue
        key_mapping = self._display.KEY_MAPPING

        keep_running = True
        if c == key_mapping[Config['key_exit']]:
            self._display.terminate()
            keep_running = False
        elif c == key_mapping[Config['key_help']]:
            self._display.show_help()
        elif c == key_mapping[Config['key_right']]:
            self._change_active_window(1)
            self._metadata_updated = False
        elif c == key_mapping[Config['key_left']]:
            self._change_active_window(-1)
            self._metadata_updated = False
        elif c == key_mapping[Config['key_up']]:
            self._get_active_menu().move(1)
            self._metadata_updated = False
        elif c == key_mapping[Config['key_down']]:
            self._get_active_menu().move(-1)
            self._metadata_updated = False
        elif c == key_mapping[Config['key_scroll_up']]:
            self._get_active_menu().move_page(1)
            self._metadata_updated = False
        elif c == key_mapping[Config['key_scroll_down']]:
            self._get_active_menu().move_page(-1)
            self._metadata_updated = False
        elif c == key_mapping[Config['key_play_selected']]:
            queue.stop()
            target = self._queue_menu.item()
            self._display.queue.jump(target)
            while self._queue_menu.selected_index > 0:
                self._queue_menu.move(1)
            queue.play()
            self._display.menus_valid = False
        elif c == key_mapping[Config['key_pause_play']] or \
                c == key_mapping[Config['key_pause_play_alt']]:
            queue.toggle()
        elif c == key_mapping[Config['key_next']]:
            queue.stop()
            queue.next()
            queue.play()
            self._display.menus_valid = False
        elif c == key_mapping[Config['key_seek_forward']] or \
                c == key_mapping[Config['key_seek_forward_alt']]:
            queue.seek(1)
        elif c == key_mapping[Config['key_seek_backward']] or \
                c == key_mapping[Config['key_seek_backward_alt']]:
            queue.seek(-1)
        elif c == key_mapping[Config['key_clear']]:
            queue.stop()
            queue.clear()
            self._display.menus_valid = False
        elif c == key_mapping[Config['key_delete']]:
            self._remove_selected_from_queue()

        return keep_running

    def refresh(self) -> None:
        """Refresh the screen and all windows.

        Overrides method from Perspective; see documentation in that class.
        """
        self._queue_window.refresh()
        self._metadata_window.refresh()

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

    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Overrides method from Perspective; see documentation in that class.
        """
        assert 0 <= self._active_window < 2

        return self._queue_menu

    def _remove_selected_from_queue(self) -> None:
        """Remove the selected player from the queue.
        """
        player = self._queue_menu.item()
        if player is not None:
            index = self._display.queue.remove(player)
            self._queue_menu.update_items(None)
            for i in range(index):
                self._get_active_menu().move(-1)
