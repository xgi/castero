import curses
import textwrap
import threading
import castero
from castero import helpers
from castero.menu import Menu
from castero.player import Player
from castero.queue import Queue
from castero.feed import Feed, FeedError, FeedLoadError, FeedDownloadError, \
    FeedParseError, FeedStructureError


class DisplayError(Exception):
    """An ambiguous error while handling the display.
    """


class DisplaySizeError(FeedError):
    """The display does not have acceptable dimensions.
    """


class Display:
    """The Display class.

    This class is used to handle all user-interaction. It creates and handles
    all aspects of the application's interface, including windows and menus. It
    retrieves input from the user and performs corresponding actions.

    This class also includes the core input loop of the application, contained
    in the loop() method.
    """
    MIN_WIDTH = 20
    MIN_HEIGHT = 8
    INPUT_TIMEOUT = 1000  # 1 second
    STATUS_TIMEOUT = 4  # multiple of INPUT_TIMEOUT

    def __init__(self, stdscr, config, feeds) -> None:
        """Initializes the object.

        Args:
            stdscr: a stdscr from curses.initscr()
            config: a loaded castero.Config object
            feeds: a loaded castero.Feeds object
        """
        self._stdscr = stdscr
        self._config = config
        self._feeds = feeds
        self._parent_x = -1
        self._parent_y = -1
        self._active_window = 0
        self._feed_window = None
        self._episode_window = None
        self._metadata_window = None
        self._header_window = None
        self._footer_window = None
        self._feed_menu = None
        self._episode_menu = None
        self._metadata_updated = False
        self._queue = Queue(config)
        self._status = ""
        self._status_timer = self.STATUS_TIMEOUT

        # basic preliminary operations
        self._stdscr.timeout(self.INPUT_TIMEOUT)
        curses.start_color()
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()
        self._stdscr.keypad(True)

        self.create_color_pairs()
        self._create_windows()
        self.create_menus()

    @staticmethod
    def create_color_pairs() -> None:
        """Initializes color pairs used for the display.

        Creates the following color pairs (foreground, background):
            - 1: yellow, black
            - 2: black, yellow
            - 3: black, white
            - 4: white, black
        """
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

    def _create_windows(self) -> None:
        """Creates and sets basic parameters for the windows.

        Creates the following windows:
            - _feed_window, _episode_window, _metadata_window
        Each window is set to use the default color pair (1), and each window
        takes up one-third of the display.
        """
        self.update_parent_dimensions()
        third_x = helpers.third(self._parent_x)

        # create windows
        self._header_window = curses.newwin(2, self._parent_x,
                                            0, 0)
        self._feed_window = curses.newwin(self._parent_y - 2, third_x,
                                          2, 0)
        self._episode_window = curses.newwin(self._parent_y - 2, third_x,
                                             2, third_x)
        self._metadata_window = curses.newwin(self._parent_y - 2, third_x,
                                              2, 2 * third_x)
        self._footer_window = curses.newwin(2, self._parent_x,
                                            self._parent_y - 2, 0)

        # set window attributes
        self._feed_window.attron(curses.color_pair(1))
        self._episode_window.attron(curses.color_pair(1))
        self._metadata_window.attron(curses.color_pair(1))
        self._header_window.attron(curses.color_pair(4))
        self._footer_window.attron(curses.color_pair(4))

    def create_menus(self) -> None:
        """Creates the menus used in each window.

        Windows which have menus should be created prior to running this method
        (using _create_windows).

        If the menus already exist when this method is run, this method will
        delete them and create new ones.
        """
        assert all(window is not None for window in [
            self._feed_window, self._episode_window
        ])

        # this method could change a lot of screen content - probably
        # reasonable to simply clear the whole screen
        self.clear()

        # delete old menus if they exist
        if self._feed_menu is not None:
            del self._feed_menu
            self._feed_menu = None
        if self._episode_menu is not None:
            del self._episode_menu
            self._episode_menu = None

        feed_items = [[]]
        episode_items = []
        for key in self._feeds:
            feed = self._feeds[key]
            feed_items[0].append(
                str(feed)
            )
            episode_items.append(
                [str(ep) for ep in feed.episodes]
            )

        self._episode_menu = Menu(self._episode_window, episode_items)
        self._feed_menu = Menu(self._feed_window, feed_items,
                               child=self._episode_menu, active=True)

        # force reset active window to prevent starting in the episodes menu
        self._active_window = 0

    def _show_help(self) -> None:
        """Show the help screen.

        This method takes over the main loop, displaying the screen until a key
        is pressed. This means that typical loop actions, including checking
        the state of the current player, will not run while this screen is up.
        """
        self.clear()
        self._stdscr.refresh()

        padding_xy = (1, 4)

        help_window = curses.newwin(self._parent_y, self._parent_x, 0, 0)
        help_window.attron(curses.A_BOLD)

        # display lines from __help__
        help_lines = castero.__help__.split('\n')
        for i in range(len(help_lines)):
            help_window.addstr(i + padding_xy[0], padding_xy[1], help_lines[i])

        help_window.refresh()

        # simply wait until any key is pressed (temporarily disable timeout)
        self._stdscr.timeout(-1)
        self._stdscr.getch()
        self._stdscr.timeout(self.INPUT_TIMEOUT)

        self.clear()

    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.
        """
        # add header
        playing_str = ""
        if self._queue.first is not None:
            state = self._queue.first.state
            if state == 0:
                playing_str = " - Stopped [%s]: " % self._queue.first.time_str
            elif state == 1:
                playing_str = " - Playing [%s]: " % self._queue.first.time_str
            elif state == 2:
                playing_str = " - Paused [%s]: " % self._queue.first.time_str
            playing_str += self._queue.first.title
            if self._queue.length > 1:
                playing_str += " (+%d in queue)" % (self._queue.length - 1)

        self._header_window.attron(curses.A_BOLD)
        self._header_window.addstr(0, 0, " " * self._parent_x)
        self._header_window.addstr(0, 0, castero.__title__ + playing_str)

        # add footer
        footer_str = ""
        if self._status == "":  # always display the status instead if needed
            if len(self._feeds) > 0:
                total_feeds = len(self._feeds)
                lengths_of_feeds = [len(self._feeds[key].episodes) for key in
                                    self._feeds]
                total_episodes = sum(lengths_of_feeds)
                median_episodes = helpers.median(lengths_of_feeds)

                footer_str += "Processed %d feeds with %d total episodes (av" \
                              "g. %d episodes, med. %d)" % (
                                  total_feeds,
                                  total_episodes,
                                  total_episodes / total_feeds,
                                  median_episodes
                              )
            else:
                footer_str += "No feeds added"
        else:
            footer_str = self._status

        footer_str += " -- Press h for help"
        self._footer_window.attron(curses.A_BOLD)
        self._footer_window.addstr(
            1, 0, " " * (self._footer_window.getmaxyx()[1] - 1)
        )
        self._footer_window.addstr(1, 0, footer_str)

        # add window titles
        self._feed_window.attron(curses.A_BOLD)
        self._episode_window.attron(curses.A_BOLD)
        self._metadata_window.attron(curses.A_BOLD)
        self._feed_window.addstr(0, 0, "Feeds")
        self._episode_window.addstr(0, 0, "Episodes")
        self._metadata_window.addstr(0, 0, "Metadata")

        # add window borders
        self._feed_window.hline(1, 0,
                                curses.ACS_HLINE,
                                self._feed_window.getmaxyx()[1] - 1)
        self._feed_window.vline(0, self._feed_window.getmaxyx()[1] - 1,
                                curses.ACS_VLINE,
                                self._feed_window.getmaxyx()[0] - 2)
        self._episode_window.hline(1, 0,
                                   curses.ACS_HLINE,
                                   self._episode_window.getmaxyx()[1] - 1)
        self._episode_window.vline(0, self._episode_window.getmaxyx()[1] - 1,
                                   curses.ACS_VLINE,
                                   self._episode_window.getmaxyx()[0] - 2)
        self._metadata_window.hline(1, 0,
                                    curses.ACS_HLINE,
                                    self._metadata_window.getmaxyx()[1] - 1)
        self._header_window.hline(1, 0,
                                  curses.ACS_HLINE,
                                  self._header_window.getmaxyx()[1])
        self._footer_window.hline(0, 0,
                                  curses.ACS_HLINE,
                                  self._footer_window.getmaxyx()[1])

        # display menu content
        self._feed_menu.display()
        self._episode_menu.display()

        # draw metadata
        if not self._metadata_updated:
            self._draw_metadata()

    def _get_input_str(self, prompt) -> str:
        """Prompts the user for input and returns the resulting string.

        This method assumes that all input strings will be obtained in the
        footer window.

        Args:
            prompt: a string to inform the user of what they need to enter

        Returns:
            str: the user's input
        """
        assert self._footer_window is not None
        assert type(prompt) == str

        curses.echo()
        curses.curs_set(1)

        self._footer_window.addstr(
            1, 0, " " * (self._footer_window.getmaxyx()[1] - 1)
        )
        self._footer_window.addstr(1, 0, prompt)
        result = self._footer_window.getstr(1, len(prompt))

        self._footer_window.clear()
        curses.curs_set(0)
        curses.noecho()

        return result.decode("utf-8")

    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Args:
            c: the input character

        Returns:
            bool: whether or not the application should continue running
        """
        keep_running = True
        if c == ord('q'):
            self.terminate()
            keep_running = False
        elif c == ord('h'):
            self._show_help()
        elif c == curses.KEY_RIGHT:
            self._change_active_window(1)
            self._metadata_updated = False
        elif c == curses.KEY_LEFT:
            self._change_active_window(-1)
            self._metadata_updated = False
        elif c == curses.KEY_UP:
            self.get_active_menu().move(1)
            self._metadata_updated = False
        elif c == curses.KEY_DOWN:
            self.get_active_menu().move(-1)
            self._metadata_updated = False
        elif c == curses.KEY_PPAGE:  # page up
            self.get_active_menu().move_page(1)
            self._metadata_updated = False
        elif c == curses.KEY_NPAGE:  # page down
            self.get_active_menu().move_page(-1)
            self._metadata_updated = False
        elif c == 10:  # return
            self._queue.stop()
            self._queue.clear()
            self._create_player_from_selected()
            self._queue.play()
            self.get_active_menu().move(-1)
        elif c == ord(' '):  # space
            self._create_player_from_selected()
            self.get_active_menu().move(-1)
        elif c == ord('c'):
            self._queue.stop()
            self._queue.clear()
        elif c == ord('p'):
            self._queue.toggle()
        elif c == ord('n'):
            self._queue.stop()
            self._queue.next()
            self._queue.play()
        elif c == ord('f'):
            self._queue.seek(1)
        elif c == ord('b'):
            self._queue.seek(-1)
        elif c == ord('a'):
            path = self._get_input_str("Enter the URL or path of the feed: ")
            try:
                # assume urls have http in them
                if "http" in path:
                    feed = Feed(url=path)
                else:
                    feed = Feed(file=path)
                if feed.validated:
                    self._feeds[path] = feed
                self.create_menus()
                self._feeds.write()
                self.update_status("Feed '%s\' successfully added" % str(feed))
            except FeedError as e:
                if type(e) == FeedLoadError:
                    self.update_status(
                        "Error: An error occurred while loading the file"
                    )
                elif type(e) == FeedDownloadError:
                    self.update_status(
                        "Error: An error occurred while downloading the feed"
                    )
                elif type(e) == FeedParseError:
                    self.update_status(
                        "Error: An error occurred while parsing the feed"
                    )
                elif type(e) == FeedStructureError:
                    self.update_status(
                        "Error: The provided feed is not a valid RSS document"
                    )
                else:
                    self.update_status(
                        "Error: An ambiguous error occurred while handling the"
                        " feed"
                    )
        elif c == ord('d'):
            if self._active_window == 0:
                deleted = self._feeds.del_at(self._feed_menu.selected_index)
                if deleted:
                    self.create_menus()
                    self._feeds.write()
                    self.update_status("Feed successfully deleted")
        elif c == ord('r'):
            t = threading.Thread(target=self._feeds.reload, args=[self])
            t.start()
        return keep_running

    def _create_player_from_selected(self) -> None:
        """Creates player(s) based on the selected items and adds to the queue.

        If the active menu is the feed menu, then this will create players for
        all episodes in the selected feed. If the active menu is the episode
        menu, this will simply create a single player.

        This method will not clear the queue prior to adding the new player(s),
        nor will it play the episodes after running.
        """
        feed_index = self._feed_menu.selected_index
        if self._active_window == 0:
            for episode in self._feeds.at(feed_index).episodes:
                player = Player(str(episode), episode.enclosure)
                self._queue.add(player)
        elif self._active_window == 1:
            episode_index = self._episode_menu.selected_index
            feed = self._feeds.at(feed_index)
            if feed is not None:
                episode = feed.episodes[episode_index]
                player = Player(str(episode), episode.enclosure)
                self._queue.add(player)

    def _change_active_window(self, direction) -> None:
        """Changes _active_window to the next or previous window, if available.

        Args:
            direction: 1 to change to the next window, -1 to change to the
                previous (if it exists)
        """
        assert direction == 1 or direction == -1

        self.get_active_menu().set_active(False)
        self._active_window += direction
        if self._active_window > 1:
            self._active_window = 1
        elif self._active_window < 0:
            self._active_window = 0
        self.get_active_menu().set_active(True)

    def _append_metadata_lines(self, string, output_lines, attr=-1,
                               add_blank=False) -> None:
        """Appends properly formatted lines to the 2D output_lines array.

        Args:
            string: the string to add to output_lines
            output_lines: 2D array, each element is [attr, str]
            attr: (optional) the attribute (i.e. curses.A_BOLD)
        """
        max_lines = int(0.7 * self._metadata_window.getmaxyx()[0])
        max_line_width = self._metadata_window.getmaxyx()[1] - 1
        lines = textwrap.wrap(string, max_line_width)

        # truncate to at most 70% of the total lines on the screen
        lines = lines[:max_lines]

        # add all lines to array
        for line in lines:
            output_lines.append([attr, line])

        # add a blank line afterward, if necessary
        if add_blank:
            output_lines.append([-1, ""])

    def _draw_metadata(self) -> None:
        """Draws the metadata of the selected feed/episode onto the window.
        """
        assert self._metadata_window is not None

        output_lines = []  # 2D array, each element is [attr, str]
        max_lines = self._metadata_window.getmaxyx()[0] - 2
        max_line_width = self._metadata_window.getmaxyx()[1] - 1

        # clear the window by drawing blank lines
        for y in range(2, self._metadata_window.getmaxyx()[0]):
            self._metadata_window.addstr(y, 0, " " * max_line_width)

        if self._active_window == 0:
            # * the selected item is a feed
            selected_index = self._feed_menu.selected_index
            feed = self._feeds.at(selected_index)

            if feed is not None:
                # draw feed title
                self._append_metadata_lines(feed.title, output_lines,
                                            attr=curses.A_BOLD)
                # draw feed lastBuildDate
                self._append_metadata_lines(feed.last_build_date, output_lines,
                                            add_blank=True)
                # draw feed link
                self._append_metadata_lines(feed.link, output_lines,
                                            add_blank=True)
                # draw feed description
                self._append_metadata_lines("Description:", output_lines,
                                            attr=curses.A_BOLD)
                self._append_metadata_lines(feed.description, output_lines,
                                            add_blank=True)
                # draw feed copyright
                self._append_metadata_lines("Copyright:", output_lines,
                                            attr=curses.A_BOLD)
                self._append_metadata_lines(feed.copyright, output_lines)

        elif self._active_window == 1:
            # * the selected item is an episode
            selected_feed_index = self._feed_menu.selected_index
            selected_episode_index = self._episode_menu.selected_index
            feed = self._feeds.at(selected_feed_index)

            if feed is not None:
                episode = feed.episodes[selected_episode_index]

                # draw episode title
                self._append_metadata_lines(episode.title, output_lines,
                                            attr=curses.A_BOLD)
                # draw episode pubdate
                self._append_metadata_lines(episode.pubdate, output_lines,
                                            add_blank=True)
                # draw episode link
                self._append_metadata_lines(episode.link, output_lines,
                                            add_blank=True)
                # draw episode description
                self._append_metadata_lines("Description:", output_lines,
                                            attr=curses.A_BOLD)
                self._append_metadata_lines(episode.description, output_lines,
                                            add_blank=True)
                # draw episode copyright
                self._append_metadata_lines("Copyright:", output_lines,
                                            attr=curses.A_BOLD)
                self._append_metadata_lines(episode.copyright, output_lines)

        y = 2
        for line in output_lines[:max_lines]:
            self._metadata_window.attrset(curses.color_pair(1))
            if line[0] != -1:
                self._metadata_window.attron(line[0])
            self._metadata_window.addstr(y, 0, line[1])
            y += 1 + line[1].count('\n')

    def get_active_window(self):
        """Retrieve the window object corresponding to the active window.

        Returns:
            curses.window: the active window object
        """
        assert 0 <= self._active_window < 3

        return {
            0: self._feed_window,
            1: self._episode_window,
            2: self._metadata_window
        }.get(self._active_window)

    def get_active_menu(self) -> Menu:
        """Retrieve the menu object corresponding to the active window.

        Returns:
            menu.Menu: the active menu object
        """
        assert 0 <= self._active_window < 2

        return {
            0: self._feed_menu,
            1: self._episode_menu,
        }.get(self._active_window)

    def clear(self) -> None:
        """Clear the screen.
        """
        self._stdscr.clear()

    def refresh(self) -> None:
        """Refresh the screen and all windows.
        """
        self._stdscr.refresh()
        self._feed_window.refresh()
        self._episode_window.refresh()
        self._metadata_window.refresh()
        self._header_window.refresh()
        self._footer_window.refresh()

    def terminate(self) -> None:
        """Set console settings to their normal state.

        This method does not, by itself, cause the application to exit. Nor
        does it even cause the input loop to end. It should simply be seen as
        a "wrapping up" method for any actions which need to be performed
        before the object is destroyed.
        """
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def update_parent_dimensions(self) -> None:
        """Update _parent_x and _parent_y to the size of the console.
        """
        self._parent_y, self._parent_x = self._stdscr.getmaxyx()

        if self._parent_y < self.MIN_HEIGHT:
            raise DisplaySizeError("Display height is too small")
        if self._parent_x < self.MIN_WIDTH:
            raise DisplaySizeError("Display width is too small")

    def getch(self) -> int:
        """Gets an input character from the user.

        This method returns after at most INPUT_TIMEOUT ms.

        Returns:
            int: the character entered by the user, or -1
        """
        c = self._stdscr.getch()
        return c

    def update_status(self, status) -> None:
        """Updates the status message displayed in the footer.

        Args:
            status: the status message to display
        """
        assert type(status) == str

        self._status = status
        self._status_timer = self.STATUS_TIMEOUT

    def update(self) -> None:
        """Updates all actively tracked components of this object.

        Should be called by the main loop after every input or input timeout.
        """
        # have the queue check if it needs to go to the next player
        self._queue.update()

        # update the status timer
        # If the user is not doing anything, the status message will take
        # INPUT_TIMEOUT * STATUS_TIMEOUT ms to be cleared. However, if the user
        # is performing inputs (i.e. traversing a menu) the message may be
        # cleared much quicker, since it will go away in STATUS_TIMEOUT
        # keypresses. However, this seems reasonable, since if the user is
        # actively controlling the client and not pausing to read the message,
        # they probably don't care about it anyway.
        if self._status_timer > 0:
            self._status_timer -= 1
            if self._status_timer <= 0:
                # status_timer should be reset during the next update_status()
                self._status = ""
