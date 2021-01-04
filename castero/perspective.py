import curses
from abc import ABC, abstractmethod

import cjkwrap

from castero.config import Config
from castero.menu import Menu


class Perspective(ABC):
    """Extendable class for display "screens".

    This class is extended by perspectives -- classes which offer methods to
    handle display elements with a certain layout. Perspectives only control
    the "inside" elements of the display: the header and footer are controlled
    by the display class.

    The user is able to switch between perspectives by using the 0-9 keys
    corresponding to the perspective's ID.

    Instances of this class do not generally hold data variables, e.g. the
    instance of the Database class. We instead reference the variables held in
    the Display instance.
    """
    ID = -1

    @abstractmethod
    def __init__(self, display):
        """
        This method does not automatically create configure some of its
        necessary elements, i.e. the windows. Instead, for some methods it is
        expected that the Display instance will call identically-named methods
        for all of its "children" perspectives when "chain" methods are called.

        For example, the Display class has a _create_windows method, which
        should call this class's create_windows method.

        Args:
            display: the parent Display instance
        """
        self._display = display

    @abstractmethod
    def create_windows(self) -> None:
        """Create and set basic parameters for the windows.
        """

    @abstractmethod
    def create_menus(self) -> None:
        """Create the menus used in each window.

        Windows which have menus should be created prior to running this method
        (using _create_windows).
        """

    @abstractmethod
    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.
        """

    @abstractmethod
    def display_all(self) -> None:
        """Force all windows to completely redraw their content.

        The normal display() method, which is used in the core UI loop, does
        not always redraw the contents of sub-features on each iteration. For
        example, it often does not draw menu contents because they only
        typically need to be drawn when the user moves within them.

        However, if the screen is cleared, the contents of these sub-features
        must be forcefully redrawn. That is what this method provides.
        """

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the screen and all windows.
        """

    @abstractmethod
    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Args:
            c: the input character

        Returns:
            bool: whether or not the application should continue running
        """

    @abstractmethod
    def made_active(self) -> None:
        """Called each time the perspective is made active (switched to).
        """

    @abstractmethod
    def update_menus(self) -> None:
        """Update/refresh the contents of all menus.
        """

    @abstractmethod
    def _invert_selected_menu(self) -> None:
        """Inverts the contents of the selected menu.
        """

    @abstractmethod
    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Returns:
            Menu: the active Menu, or None
        """

    def _generic_handle_input(self, c) -> bool:
        """Generic handler for performing actions corresponding to input.

        Args:
            c: the input character

        Returns:
            bool: whether or not the application should continue running
        """
        queue = self._display.queue
        key_mapping = self._display.KEY_MAPPING

        keep_running = True
        if c == key_mapping[Config['key_exit']]:
            self.update_current_episode_progress()
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
        elif c == key_mapping[Config['key_clear']]:
            self.update_current_episode_progress()
            queue.stop()
            queue.clear()
        elif c == key_mapping[Config['key_pause_play']] or \
                c == key_mapping[Config['key_pause_play_alt']]:
            self.update_current_episode_progress()
            queue.toggle()
        elif c == key_mapping[Config['key_next']]:
            self.update_current_episode_progress()
            queue.stop()
            queue.next()
            queue.play()
        elif c == key_mapping[Config['key_seek_forward']] or \
                c == key_mapping[Config['key_seek_forward_alt']]:
            queue.seek(1)
            self.update_current_episode_progress()
        elif c == key_mapping[Config['key_seek_backward']] or \
                c == key_mapping[Config['key_seek_backward_alt']]:
            queue.seek(-1)
            self.update_current_episode_progress()
        elif c == key_mapping[Config['key_volume_increase']]:
            queue.change_volume(1)
        elif c == key_mapping[Config['key_volume_decrease']]:
            queue.change_volume(-1)
        elif c == key_mapping[Config['key_rate_increase']]:
            queue.change_rate(1, display=self._display)
        elif c == key_mapping[Config['key_rate_decrease']]:
            queue.change_rate(-1, display=self._display)
        elif c == key_mapping[Config['key_add_feed']]:
            self._display.add_feed()
        elif c == key_mapping[Config['key_remove']]:
            if self._active_window == 0:
                self._display.delete_feed(self._feed_menu.item)
                self.update_menus()
        elif c == key_mapping[Config['key_reload']]:
            self._display.reload_feeds()
        elif c == key_mapping[Config['key_reload_selected']]:
            feed = self._feed_menu.item
            if feed is not None:
                self._display.reload_selected_feed(feed)
        elif c == key_mapping[Config['key_show_url']]:
            if self._active_window == 1 and self._episode_menu.item:
                self._display.show_episode_url(self._episode_menu.item)
        elif c == key_mapping[Config['key_save']]:
            if self._active_window == 0 and self._feed_menu.item:
                self._display.save_episodes(feed=self._feed_menu.item)
            elif self._active_window == 1 and self._episode_menu.item:
                self._display.save_episodes(episode=self._episode_menu.item)
        elif c == key_mapping[Config['key_delete']]:
            if self._active_window == 0 and self._feed_menu.item:
                self._display.delete_episodes(feed=self._feed_menu.item)
            elif self._active_window == 1 and self._episode_menu.item:
                self._display.delete_episodes(episode=self._episode_menu.item)
        elif c == key_mapping[Config['key_execute']]:
            if self._active_window == 1 and self._episode_menu.item:
                self._display.execute_command(self._episode_menu.item)
        elif c == key_mapping[Config['key_invert']]:
            self._invert_selected_menu()
        elif c == key_mapping[Config['key_filter']]:
            menu = self._get_active_menu()
            if menu.filter_text:
                menu.filter_text = ""
            else:
                self._display.filter_menu(menu)
            self.update_menus()
            menu.move(-1)
            menu.move(1)
        elif c == key_mapping[Config['key_mark_played']]:
            if self._active_window == 0:
                feed = self._feed_menu.item
                if feed is not None:
                    episodes = self._display.database.episodes(feed)
                    for episode in episodes:
                        episode.played = not episode.played
                        self._clear_episode_progress(episode)
                    self._display.modified_episodes.extend(episodes)
            elif self._active_window == 1:
                episode = self._episode_menu.item
                if episode is not None:
                    episode.played = not episode.played
                    self._display.modified_episodes.append(episode)
                    self._episode_menu.move(-1)
                    self._clear_episode_progress(episode)

        return keep_running

    def _change_active_window(self, direction) -> None:
        """Changes _active_window to the next or previous window, if available.

        Args:
            direction: 1 to change to the next window, -1 to change to the
                previous (if it exists)
        """
        assert direction == 1 or direction == -1

        active_menu = self._get_active_menu()
        if active_menu is not None:
            active_menu.set_active(False)

        self._active_window += direction
        if self._active_window > 1:
            self._active_window = 1
        elif self._active_window < 0:
            self._active_window = 0

        new_active_menu = self._get_active_menu()
        if new_active_menu is not None:
            new_active_menu.set_active(True)

    def _draw_metadata(self, window) -> None:
        """Draws the metadata of the selected feed/episode onto the window.

        Args:
            window: the curses window which will display the metadata
        """
        assert window is not None

        max_lines = window.getmaxyx()[0] - 4
        max_line_width = window.getmaxyx()[1] - 1

        # clear the window by drawing blank lines
        for y in range(2, window.getmaxyx()[0] - 2):
            window.addstr(y, 0, " " * max_line_width)

        metadata = self._get_active_menu().metadata
        temp_lines = metadata.split('\n')

        lines = []
        for line in temp_lines:
            parts = cjkwrap.wrap(line, window.getmaxyx()[1] - 1,
                                 replace_whitespace=True)
            if len(parts) == 0:
                lines.append('')
            else:
                for part in parts:
                    lines.append(part.strip())

        y = 2
        for line in lines[:max_lines]:
            attr = curses.color_pair(1)
            if line.startswith('!cb'):
                attr |= curses.A_BOLD
                line = line[3:]

            window.addstr(y, 0, line, attr)
            y += 1

    def update_current_episode_progress(self) -> None:
        """Update progress of the first player in queue
        """
        (episode, progress) = self._display.queue.get_episode_progress()
        if episode is not None and progress is not None:
            episode.progress = progress
            self._display.database.replace_progress(episode, progress)

    def _clear_episode_progress(self, episode) -> None:
        """remove progress of the episode

        Args:
            episode: the episode to clear progress from
        """
        self._display.database.delete_progress(episode)
