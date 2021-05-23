import curses

from castero import helpers
from castero.config import Config
from castero.menu import Menu
from castero.menus.chronomenu import ChronoMenu
from castero.perspective import Perspective
from castero.player import Player


class ChronoPerspective(Perspective):
    """The chronological perspective.

    This class handles display elements while in the chronological perspective,
    which is a listing of episodes from all feeds ordered chronologically.
    """
    ID = 5

    def __init__(self, display) -> None:
        """
        Overrides method from Perspective; see documentation in that class.
        """
        super().__init__(display)
        self._active_window = 0
        self._episode_window = None
        self._metadata_window = None
        self._episode_menu = None
        self._metadata_updated = False

    def create_windows(self) -> None:
        """Create and set basic parameters for the windows.

        Overrides method from Perspective; see documentation in that class.
        """
        # delete old windows if they exist
        if self._episode_window is not None:
            del self._episode_window
            self._episode_window = None
        if self._metadata_window is not None:
            del self._metadata_window
            self._metadata_window = None

        parent_x = self._display.parent_x
        parent_y = self._display.parent_y
        third_x = helpers.third(parent_x)
        self._episode_window = curses.newwin(parent_y - 2, third_x * 2,
                                             2, 0)
        metadata_width = parent_x - ((third_x * 2) - 1)
        self._metadata_window = curses.newwin(parent_y - 3, metadata_width,
                                              2, 2 * third_x)

        # update menus if necessary
        if self._episode_menu is not None:
            self._episode_menu.window = self._episode_window

    def create_menus(self) -> None:
        """Create the menus used in each window.

        Overrides method from Perspective; see documentation in that class.
        """
        assert all(window is not None for window in [
            self._episode_window
        ])

        self._episode_menu = ChronoMenu(
            self._episode_window, self._display.database, active=True)

    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.

        Overrides method from Perspective; see documentation in that class.
        """
        # clear dynamic menu headers
        self._episode_window.addstr(
            0, 0, " " * self._episode_window.getmaxyx()[1])

        # add window headers
        self._episode_window.addstr(
            0, 0, self._episode_menu.title,
            curses.color_pair(7) | curses.A_BOLD)
        self._metadata_window.addstr(
            0, 0, "Metadata",
            curses.color_pair(7) | curses.A_BOLD)

        # add window borders
        self._episode_window.hline(
            1, 0,
            0, self._episode_window.getmaxyx()[1],
            curses.ACS_HLINE | curses.color_pair(8))
        self._metadata_window.hline(
            1, 0,
            0, self._metadata_window.getmaxyx()[1] - 1,
            curses.ACS_HLINE | curses.color_pair(8))
        if not helpers.is_true(Config["disable_vertical_borders"]):
            self._episode_window.vline(
                0, self._episode_window.getmaxyx()[1] - 1,
                0, self._episode_window.getmaxyx()[0] - 2,
                curses.ACS_VLINE | curses.color_pair(8))

        # draw metadata
        if not self._metadata_updated:
            self._draw_metadata(self._metadata_window)
            self._metadata_window.refresh()
            self._metadata_updated = True

        self._episode_window.refresh()

    def display_all(self) -> None:
        """Force all windows to completely redraw their content.

        Overrides method from Perspective; see documentation in that class.
        """
        self._metadata_updated = False
        self._episode_menu.display()
        self.display()

    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Overrides method from Perspective; see documentation in that class.
        """
        queue = self._display.queue
        key_mapping = self._display.KEY_MAPPING

        keep_running = True
        if c == key_mapping[Config['key_play_selected']]:
            queue.stop()
            queue.clear()
            self._create_player_from_selected()
            queue.play()
        elif c == key_mapping[Config['key_add_selected']]:
            self._create_player_from_selected()
            self._get_active_menu().move(-1)
        elif c == key_mapping[Config['key_show_url']]:
            if self._episode_menu.item:
                self._display.show_episode_url(self._episode_menu.item)
        elif c == key_mapping[Config['key_save']]:
            if self._episode_menu.item:
                self._display.save_episodes(episode=self._episode_menu.item)
                self._display.menus_valid = False
        elif c == key_mapping[Config['key_delete']]:
            if self._episode_menu.item:
                self._display.delete_episodes(episode=self._episode_menu.item)
                self._display.menus_valid = False
        elif c == key_mapping[Config['key_mark_played']]:
            if self._active_window == 0:
                episode = self._episode_menu.item
                if episode is not None:
                    episode.played = not episode.played
                    self._display.modified_episodes.append(episode)
                    self._episode_menu.move(-1)
        elif c == key_mapping[Config['key_execute']]:
            episode = self._episode_menu.item
            if episode is not None:
                self._display.execute_command(episode)
        elif c == key_mapping[Config['key_reload_selected']]:
            pass
        elif c == key_mapping[Config['key_remove']]:
            pass
        else:
            keep_running = self._generic_handle_input(c)

        return keep_running

    def made_active(self) -> None:
        """Called each time the perspective is made active (switched to).

        Overrides method from Perspective; see documentation in that class.
        """

    def update_menus(self) -> None:
        """Update/refresh the contents of all menus.

        Overrides method from Perspective; see documentation in that class.
        """
        self._episode_menu.update_items(None)
        self._metadata_updated = False

    def refresh(self) -> None:
        """Refresh the screen and all windows.

        Overrides method from Perspective; see documentation in that class.
        """
        self._episode_window.refresh()
        self._metadata_window.refresh()
        self._episode_menu.refresh()

    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Overrides method from Perspective; see documentation in that class.
        """
        assert 0 <= self._active_window < 2

        return self._episode_menu

    def _invert_selected_menu(self) -> None:
        """Inverts the contents of the selected menu.

        Overrides method from Perspective; see documentation in that class.
        """
        self._get_active_menu().invert()
        self._metadata_updated = False

    def _create_player_from_selected(self) -> None:
        """Creates player(s) based on the selected items and adds to the queue.

        If the active menu is the feed menu, then this will create players for
        all episodes in the selected feed. If the active menu is the episode
        menu, this will simply create a single player.

        This method will not clear the queue prior to adding the new player(s),
        nor will it play the episodes after running.
        """
        episode = self._episode_menu.item
        if episode is not None:
            player = Player.create_instance(
                self._display.AVAILABLE_PLAYERS, str(episode),
                episode.get_playable(), episode)
            self._display.queue.add(player)
        self._metadata_updated = False
