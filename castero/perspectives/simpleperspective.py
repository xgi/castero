import curses

from castero import helpers
from castero.config import Config
from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu
from castero.menus.feedmenu import FeedMenu
from castero.perspective import Perspective
from castero.player import Player


class SimplePerspective(Perspective):
    """The SimplePerspective class.

    This class handles display elements while in the simple perspective, which
    is similar to the primary perspective but without a metadata window.
    """
    ID = 3

    def __init__(self, display) -> None:
        """Initializes the object.

        Overrides method from Perspective; see documentation in that class.
        """
        super().__init__(display)
        self._active_window = 0
        self._feed_window = None
        self._episode_window = None
        self._feed_menu = None
        self._episode_menu = None

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
        

        fw_width = min(25, parent_x / 2)

        self._feed_window = curses.newwin(parent_y - 2, fw_width,
                                          2, 0)
        self._episode_window = curses.newwin(parent_y - 2, parent_x - fw_width,
                                             2, fw_width)

        self._feed_window.attron(curses.color_pair(1))
        self._episode_window.attron(curses.color_pair(1))

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
        # add window titles
        self._feed_window.attron(curses.A_BOLD)
        self._episode_window.attron(curses.A_BOLD)
        self._feed_window.addstr(0, 0, "Feeds")
        self._episode_window.addstr(0, 0, "Episodes")

        # add window borders
        self._feed_window.hline(1, 0,
                                0, self._feed_window.getmaxyx()[1])
        self._episode_window.hline(1, 0,
                                   0, self._episode_window.getmaxyx()[1])
        if not helpers.is_true(Config["disable_vertical_borders"]):
            self._feed_window.vline(0, self._feed_window.getmaxyx()[1] - 1,
                                    0, self._feed_window.getmaxyx()[0] - 2)

        # display menu content
        self._feed_menu.display()
        self._episode_menu.display()

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
            queue.clear()
            self._create_player_from_selected()
            queue.play()
        elif c == key_mapping[Config['key_add_selected']]:
            self._create_player_from_selected()
            self._get_active_menu().move(-1)
        elif c == key_mapping[Config['key_clear']]:
            queue.stop()
            queue.clear()
        elif c == key_mapping[Config['key_pause_play']] or \
                c == key_mapping[Config['key_pause_play_alt']]:
            queue.toggle()
        elif c == key_mapping[Config['key_next']]:
            queue.stop()
            queue.next()
            queue.play()
        elif c == key_mapping[Config['key_seek_forward']] or \
                c == key_mapping[Config['key_seek_forward_alt']]:
            queue.seek(1)
        elif c == key_mapping[Config['key_seek_backward']] or \
                c == key_mapping[Config['key_seek_backward_alt']]:
            queue.seek(-1)
        elif c == key_mapping[Config['key_add_feed']]:
            self._display.add_feed()
        elif c == key_mapping[Config['key_delete']]:
            if self._active_window == 0:
                self._display.delete_feed(self._feed_menu.item())
                self._feed_menu.update_child()
        elif c == key_mapping[Config['key_reload']]:
            self._display.reload_feeds()
        elif c == key_mapping[Config['key_save']]:
            if self._active_window == 0 and self._feed_menu.item():
                self._display.save_episodes(feed=self._feed_menu.item())
            elif self._active_window == 1 and self._episode_menu.item():
                self._display.save_episodes(episode=self._episode_menu.item())
        elif c == key_mapping[Config['key_invert']]:
            self._invert_selected_menu()
        elif c == key_mapping[Config['key_mark_played']]:
            if self._active_window == 0:
                feed = self._feed_menu.item()
                if feed is not None:
                    episodes = self._display.database.episodes(feed)
                    for episode in episodes:
                        episode.played = not episode.played
                    self._display.modified_episodes.extend(episodes)
            elif self._active_window == 1:
                episode = self._episode_menu.item()
                if episode is not None:
                    episode.played = not episode.played
                    self._display.modified_episodes.append(episode)
                    self._episode_menu.move(-1)

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

    def refresh(self) -> None:
        """Refresh the screen and all windows.

        Overrides method from Perspective; see documentation in that class.
        """
        self._feed_window.refresh()
        self._episode_window.refresh()

    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Overrides method from Perspective; see documentation in that class.
        """
        assert 0 <= self._active_window < 2

        return {
            0: self._feed_menu,
            1: self._episode_menu,
        }.get(self._active_window)

    def _create_player_from_selected(self) -> None:
        """Creates player(s) based on the selected items and adds to the queue.

        If the active menu is the feed menu, then this will create players for
        all episodes in the selected feed. If the active menu is the episode
        menu, this will simply create a single player.

        This method will not clear the queue prior to adding the new player(s),
        nor will it play the episodes after running.
        """
        if self._active_window == 0:
            feed = self._feed_menu.item()
            if feed is not None:
                for episode in self._display.database.episodes(feed):
                    player = Player.create_instance(
                        self._display.AVAILABLE_PLAYERS, str(episode),
                        episode.get_playable(), episode)
                    self._display.queue.add(player)
        elif self._active_window == 1:
            episode = self._episode_menu.item()
            if episode is not None:
                player = Player.create_instance(
                    self._display.AVAILABLE_PLAYERS, str(episode),
                    episode.get_playable(), episode)
                self._display.queue.add(player)

    def _invert_selected_menu(self) -> None:
        """Inverts the contents of the selected menu.
        """
        self._get_active_menu().invert()
        if self._feed_menu:
            self._feed_menu.update_child()
