import curses

from castero import helpers
from castero.config import Config
from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu
from castero.menus.feedmenu import FeedMenu
from castero.perspective import Perspective
from castero.player import Player


class SimplePerspective(Perspective):
    """The simple perspective, similar to the primary one.

    This class handles display elements while in the simple perspective, which
    is similar to the primary perspective but without a metadata window.
    """
    ID = 3

    def __init__(self, display) -> None:
        """
        Overrides method from Perspective; see documentation in that class.
        """
        super().__init__(display)
        self._active_window = 0
        self._feed_window = None
        self._episode_window = None
        self._feed_menu = None
        self._episode_menu = None
        self._queue_unplayed_feed_episodes = helpers.is_true(
            Config["add_only_unplayed_episodes"])

    def create_windows(self) -> None:
        """Create and set basic parameters for the windows.

        Overrides method from Perspective; see documentation in that class.
        """
        # delete old windows if they exist
        if self._feed_window is not None:
            del self._feed_window
            self._feed_window = None
        if self._episode_window is not None:
            del self._episode_window
            self._episode_window = None

        parent_x = self._display.parent_x
        parent_y = self._display.parent_y

        fw_width = min(25, parent_x // 2)

        self._feed_window = curses.newwin(parent_y - 2, fw_width,
                                          2, 0)
        self._episode_window = curses.newwin(parent_y - 2, parent_x - fw_width,
                                             2, fw_width)

        # update menus if necessary
        if self._feed_menu is not None:
            self._feed_menu.window = self._feed_window
        if self._episode_menu is not None:
            self._episode_menu.window = self._episode_window

    def create_menus(self) -> None:
        """Create the menus used in each window, if necessary.

        Overrides method from Perspective; see documentation in that class.
        """
        assert all(window is not None for window in [
            self._feed_window, self._episode_window
        ])

        self._episode_menu = EpisodeMenu(
            self._episode_window, self._display.database)
        self._feed_menu = FeedMenu(self._feed_window, self._display.database,
                                   child=self._episode_menu, active=True)

    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.

        Overrides method from Perspective; see documentation in that class.
        """
        # clear dynamic menu headers
        self._feed_window.addstr(0, 0, " " * self._feed_window.getmaxyx()[1])
        self._episode_window.addstr(0, 0,
                                    " " * self._episode_window.getmaxyx()[1])

        # add window headers
        self._feed_window.addstr(0, 0, self._feed_menu.title,
                                 curses.color_pair(7) | curses.A_BOLD)
        self._episode_window.addstr(0, 0, self._episode_menu.title,
                                    curses.color_pair(7) | curses.A_BOLD)

        # add window borders
        self._feed_window.hline(1, 0,
                                0, self._feed_window.getmaxyx()[1],
                                curses.ACS_HLINE | curses.color_pair(8))
        self._episode_window.hline(1, 0,
                                   0, self._episode_window.getmaxyx()[1],
                                   curses.ACS_HLINE | curses.color_pair(8))
        if not helpers.is_true(Config["disable_vertical_borders"]):
            self._feed_window.vline(0, self._feed_window.getmaxyx()[1] - 1,
                                    0, self._feed_window.getmaxyx()[0] - 2,
                                    curses.ACS_VLINE | curses.color_pair(8))

        self._feed_window.refresh()
        self._episode_window.refresh()

    def display_all(self) -> None:
        """Force all windows to completely redraw their content.

        Overrides method from Perspective; see documentation in that class.
        """
        self._metadata_updated = False
        self._feed_menu.display()
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
        elif c == key_mapping[Config['key_clear_progress']]:
            self._clear_progress_from_selected()
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
        self._feed_menu.update_items(None)
        self._feed_menu.update_child()
        self._metadata_updated = False

    def refresh(self) -> None:
        """Refresh the screen and all windows.

        Overrides method from Perspective; see documentation in that class.
        """
        self._feed_window.refresh()
        self._episode_window.refresh()
        self._feed_menu.refresh()

    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Overrides method from Perspective; see documentation in that class.
        """
        assert 0 <= self._active_window < 2

        return {
            0: self._feed_menu,
            1: self._episode_menu,
        }.get(self._active_window)

    def _invert_selected_menu(self) -> None:
        """Inverts the contents of the selected menu.

        Overrides method from Perspective; see documentation in that class.
        """
        self._get_active_menu().invert()
        if self._feed_menu:
            self._feed_menu.update_child()
        self._metadata_updated = False

    def _create_player_from_selected(self) -> None:
        """Creates player(s) based on the selected items and adds to the queue.

        If the active menu is the feed menu, then this will create players for
        all episodes in the selected feed. If the active menu is the episode
        menu, this will simply create a single player.

        This method will not clear the queue prior to adding the new player(s),
        nor will it play the episodes after running.
        """
        if self._active_window == 0:
            feed = self._feed_menu.item
            if feed is not None:
                if self._queue_unplayed_feed_episodes:
                    episodes = self._display.database.unplayed_episodes(feed)
                else:
                    episodes = self._display.database.episodes(feed)

                for episode in episodes:
                    player = Player.create_instance(
                        self._display.AVAILABLE_PLAYERS, str(episode),
                        episode.get_playable(), episode)
                    self._display.queue.add(player)
        elif self._active_window == 1:
            episode = self._episode_menu.item
            if episode is not None:
                player = Player.create_instance(
                    self._display.AVAILABLE_PLAYERS, str(episode),
                    episode.get_playable(), episode)
                self._display.queue.add(player)
        self._metadata_updated = False

    def _clear_progress_from_selected(self) -> None:
        if self._active_window == 1:
            episode = self._episode_menu.item
            if episode is not None:
                self._display.database.delete_progress(episode)
                self._episode_window.refresh()
