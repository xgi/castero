import curses

from castero import helpers
from castero.menu import Menu
from castero.menus.episodemenu import EpisodeMenu
from castero.perspective import Perspective
from castero.player import Player


class Primary(Perspective):
    """The Primary class.

    This class handles display elements while in the primary perspective, which
    is the default perspective.
    """
    ID = 1

    def __init__(self, display) -> None:
        """Initializes the object.

        Overrides method from Perspective; see documentation in that class.
        """
        super().__init__(display)
        self._active_window = 0
        self._feed_window = None
        self._episode_window = None
        self._metadata_window = None
        self._feed_menu = None
        self._episode_menu = None
        self._metadata_updated = False

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
        if self._metadata_window is not None:
            del self._metadata_window
            self._metadata_window = None

        parent_x = self._display.parent_x
        parent_y = self._display.parent_y
        third_x = helpers.third(parent_x)
        self._feed_window = curses.newwin(parent_y - 2, third_x,
                                          2, 0)
        self._episode_window = curses.newwin(parent_y - 2, third_x,
                                             2, third_x)
        metadata_width = parent_x - ((third_x * 2) - 1)
        self._metadata_window = curses.newwin(parent_y - 2, metadata_width,
                                              2, 2 * third_x)

        self._feed_window.attron(curses.color_pair(1))
        self._episode_window.attron(curses.color_pair(1))
        self._metadata_window.attron(curses.color_pair(1))

    def create_menus(self) -> None:
        """Create the menus used in each window, if necessary.

        Overrides method from Perspective; see documentation in that class.
        """
        assert all(window is not None for window in [
            self._feed_window, self._episode_window
        ])

        # this method could change a lot of screen content - probably
        # reasonable to simply clear the whole screen
        self._display.clear()

        # delete old menus if they exist
        if self._feed_menu is not None:
            del self._feed_menu
            self._feed_menu = None
        if self._episode_menu is not None:
            del self._episode_menu
            self._episode_menu = None

        feed_items = [[]]
        for key in self._display.feeds:
            feed = self._display.feeds[key]
            feed_items[0].append(
                str(feed)
            )

        self._episode_menu = EpisodeMenu(self._episode_window, self._display._feeds,
                                         config = self._display.config)
        self._feed_menu = Menu(self._feed_window, feed_items,
                               child=self._episode_menu, active=True)

        # force reset active window to prevent starting in the episodes menu
        self._active_window = 0

    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.

        Overrides method from Perspective; see documentation in that class.
        """
        # add window titles
        self._feed_window.attron(curses.A_BOLD)
        self._episode_window.attron(curses.A_BOLD)
        self._metadata_window.attron(curses.A_BOLD)
        self._feed_window.addstr(0, 0, "Feeds")
        self._episode_window.addstr(0, 0, "Episodes")
        self._metadata_window.addstr(0, 0, "Metadata")

        # add window borders
        self._feed_window.hline(1, 0,
                                0, self._feed_window.getmaxyx()[1] - 1)
        self._feed_window.vline(0, self._feed_window.getmaxyx()[1] - 1,
                                0, self._feed_window.getmaxyx()[0] - 2)
        self._episode_window.hline(1, 0,
                                   0, self._episode_window.getmaxyx()[1] - 1)
        self._episode_window.vline(0, self._episode_window.getmaxyx()[1] - 1,
                                   0, self._episode_window.getmaxyx()[0] - 2)
        self._metadata_window.hline(1, 0,
                                    0, self._metadata_window.getmaxyx()[1] - 1)

        # display menu content
        self._feed_menu.display()
        self._episode_menu.display()

        # draw metadata
        if not self._metadata_updated:
            selected_feed_index = self._feed_menu.selected_index
            feed = self._display.feeds.at(selected_feed_index)
            if feed is not None:
                if self._active_window == 0:
                    self._draw_metadata(self._metadata_window, feed=feed)
                elif self._active_window == 1:
                    selected_episode_index = self._episode_menu.selected_index
                    episode = feed.episodes[selected_episode_index]
                    self._draw_metadata(self._metadata_window, episode=episode)

    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Overrides method from Perspective; see documentation in that class.
        """
        config = self._display.config
        queue = self._display.queue
        key_mapping = self._display.KEY_MAPPING

        keep_running = True
        if c == key_mapping[config['key_exit']]:
            self._display.terminate()
            keep_running = False
        elif c == key_mapping[config['key_help']]:
            self._display.show_help()
        elif c == key_mapping[config['key_right']]:
            self._change_active_window(1)
            self._metadata_updated = False
        elif c == key_mapping[config['key_left']]:
            self._change_active_window(-1)
            self._metadata_updated = False
        elif c == key_mapping[config['key_up']]:
            self._get_active_menu().move(1)
            self._metadata_updated = False
        elif c == key_mapping[config['key_down']]:
            self._get_active_menu().move(-1)
            self._metadata_updated = False
        elif c == key_mapping[config['key_scroll_up']]:
            self._get_active_menu().move_page(1)
            self._metadata_updated = False
        elif c == key_mapping[config['key_scroll_down']]:
            self._get_active_menu().move_page(-1)
            self._metadata_updated = False
        elif c == key_mapping[config['key_play_selected']]:
            queue.stop()
            queue.clear()
            self._create_player_from_selected()
            queue.play()
        elif c == key_mapping[config['key_add_selected']]:
            self._create_player_from_selected()
            self._get_active_menu().move(-1)
        elif c == key_mapping[config['key_clear']]:
            queue.stop()
            queue.clear()
        elif c == key_mapping[config['key_pause_play']] or \
                c == key_mapping[config['key_pause_play_alt']]:
            queue.toggle()
        elif c == key_mapping[config['key_next']]:
            queue.stop()
            queue.next()
            queue.play()
        elif c == key_mapping[config['key_seek_forward']] or \
                c == key_mapping[config['key_seek_forward_alt']]:
            queue.seek(1)
        elif c == key_mapping[config['key_seek_backward']] or \
                c == key_mapping[config['key_seek_backward_alt']]:
            queue.seek(-1)
        elif c == key_mapping[config['key_add_feed']]:
            self._display.add_feed()
        elif c == key_mapping[config['key_delete']]:
            if self._active_window == 0:
                self._display.delete_feed(self._feed_menu.selected_index)
        elif c == key_mapping[config['key_reload']]:
            self._display.reload_feeds()
        elif c == key_mapping[config['key_save']]:
            feed_index = self._feed_menu.selected_index
            episode_index = self._episode_menu.selected_index if \
                self._active_window == 1 else None
            self._display.save_episodes(feed_index, episode_index)
        elif c == key_mapping[config['key_invert']]:
            self._invert_selected_menu()

        return keep_running

    def made_active(self) -> None:
        """Called each time the perspective is made active (switched to).

        Overrides method from Perspective; see documentation in that class.
        """

    def refresh(self) -> None:
        """Refresh the screen and all windows.

        Overrides method from Perspective; see documentation in that class.
        """
        self._feed_window.refresh()
        self._episode_window.refresh()
        self._metadata_window.refresh()

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
        feed_index = self._feed_menu.selected_index
        feed = self._display.feeds.at(feed_index)
        if self._active_window == 0:
            if feed is not None:
                for episode in feed.episodes:
                    player = Player(str(episode), episode.get_playable(),
                                    episode)
                    self._display.queue.add(player)
        elif self._active_window == 1:
            episode_index = self._episode_menu.selected_index
            if feed is not None:
                episode = feed.episodes[episode_index]
                player = Player(str(episode), episode.get_playable(), episode)
                self._display.queue.add(player)

    def _invert_selected_menu(self) -> None:
        """Inverts the contents of the selected menu.
        """
        feed_index = self._feed_menu.selected_index
        if self._active_window == 0:
            self._display.feeds.sort(toggle_invert=True)
            self.create_menus()
        elif self._active_window == 1:
            feed = self._display.feeds.at(feed_index)
            if feed is not None:
                feed.invert_episodes()
                self._display.feeds.write()
                self.create_menus()
                for i in range(feed_index):
                    self._feed_menu.move(-1)
                self._change_active_window(1)
