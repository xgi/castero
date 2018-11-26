import curses
import glob
import importlib
import threading
from os.path import dirname, basename, isfile

import castero
from castero import helpers
from castero.config import Config
from castero.downloadqueue import DownloadQueue
from castero.feed import Feed, FeedError, FeedLoadError, FeedDownloadError, \
    FeedParseError, FeedStructureError
from castero.feeds import Feeds
from castero.perspective import Perspective
from castero.queue import Queue


class DisplayError(Exception):
    """An ambiguous error while handling the display.
    """


class DisplaySizeError(DisplayError):
    """The display does not have acceptable dimensions.
    """


class Display:
    """The Display class.

    This class is used to handle all user-interaction. It creates and handles
    all aspects of the application's interface, including windows and menus. It
    retrieves input from the user and performs corresponding actions.
    """
    MIN_WIDTH = 20
    MIN_HEIGHT = 8
    INPUT_TIMEOUT = 1000  # 1 second
    STATUS_TIMEOUT = 4  # multiple of INPUT_TIMEOUT
    AVAILABLE_COLORS = {
        'black': curses.COLOR_BLACK,
        'blue': curses.COLOR_BLUE,
        'cyan': curses.COLOR_CYAN,
        'green': curses.COLOR_GREEN,
        'magenta': curses.COLOR_MAGENTA,
        'red': curses.COLOR_RED,
        'white': curses.COLOR_WHITE,
        'yellow': curses.COLOR_YELLOW,
        'transparent': -1
    }
    KEY_MAPPING = {chr(i): i for i in range(256)}
    KEY_MAPPING.update(
        (name[4:], value) for name, value in vars(curses).items()
        if name.startswith('KEY_')
    )
    KEY_MAPPING.update(
        {
            'ENTER': 10,
            'SPACE': 32
        }
    )

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
        self._perspectives = {}
        self._active_perspective = 1
        self._header_window = None
        self._footer_window = None
        self._queue = Queue(config)
        self._download_queue = DownloadQueue(self)
        self._status = ""
        self._status_timer = self.STATUS_TIMEOUT

        # basic preliminary operations
        self._stdscr.timeout(self.INPUT_TIMEOUT)
        curses.start_color()
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()
        self._stdscr.keypad(True)

        self.update_parent_dimensions()
        self.create_color_pairs()
        self._load_perspectives()
        self._create_windows()
        self.create_menus()

    def create_color_pairs(self) -> None:
        """Initializes color pairs used for the display.

        Creates the following color pairs (foreground, background):
            - 1: foreground, background
            - 2: background, foreground
            - 3: background_alt, foreground_alt
            - 4: foreground_alt, background_alt
        """
        assert self._config["color_foreground"] in self.AVAILABLE_COLORS
        assert self._config["color_background"] in self.AVAILABLE_COLORS
        assert self._config["color_foreground_alt"] in self.AVAILABLE_COLORS
        assert self._config["color_background_alt"] in self.AVAILABLE_COLORS

        if (self.AVAILABLE_COLORS[self._config["color_background"]] == -1 or self.AVAILABLE_COLORS[self._config["color_background_alt"]] == -1):
            curses.use_default_colors()

        curses.init_pair(
            1,
            self.AVAILABLE_COLORS[self._config["color_foreground"]],
            self.AVAILABLE_COLORS[self._config["color_background"]]
        )
        curses.init_pair(
            2,
            self.AVAILABLE_COLORS[self._config["color_background"]],
            self.AVAILABLE_COLORS[self._config["color_foreground"]]
        )
        curses.init_pair(
            3,
            self.AVAILABLE_COLORS[self._config["color_background_alt"]],
            self.AVAILABLE_COLORS[self._config["color_foreground_alt"]]
        )
        curses.init_pair(
            4,
            self.AVAILABLE_COLORS[self._config["color_foreground_alt"]],
            self.AVAILABLE_COLORS[self._config["color_background_alt"]]
        )

    """Load instances of perspectives from the `perspectives` package.
    """

    def _load_perspectives(self) -> None:
        # load a list of modules names by manually detecting .py files
        module_files = glob.glob(dirname(__file__) + "/perspectives/*.py")
        module_names = [basename(f)[:-3] for f in module_files if isfile(f)]

        for name in module_names:
            p_mod = importlib.import_module("castero.perspectives.%s" % name)
            p_cls = getattr(
                p_mod,
                dir(p_mod)[[cls.lower() == name
                            for cls in dir(p_mod)].index(True)])
            cls = p_cls(self)
            self._perspectives[cls.ID] = cls

    def _create_windows(self) -> None:
        """Creates and sets basic parameters for the windows.

        If the windows already exist when this method is run, this method will
        delete them and create new ones.
        """
        # delete old windows if they exist
        if self._header_window is not None:
            del self._header_window
            self._header_window = None
        if self._footer_window is not None:
            del self._footer_window
            self._footer_window = None

        # create windows
        self._header_window = curses.newwin(2, self._parent_x,
                                            0, 0)
        self._footer_window = curses.newwin(2, self._parent_x,
                                            self._parent_y - 2, 0)

        # set window attributes
        self._header_window.attron(curses.color_pair(4))
        self._footer_window.attron(curses.color_pair(4))

        # create windows for all perspectives
        for perspective_id in self._perspectives:
            self._perspectives[perspective_id].create_windows()

    def create_menus(self) -> None:
        """Creates the menus used in each window.

        Windows which have menus should be created prior to running this method
        (using _create_windows).

        If the menus already exist when this method is run, this method will
        delete them and create new ones.
        """
        for perspective_id in self._perspectives:
            self._perspectives[perspective_id].create_menus()

    def show_help(self) -> None:
        """Show the help screen.

        This method takes over the main loop, displaying the screen until a key
        is pressed. This means that typical loop actions, including checking
        the state of the current player, will not run while this screen is up.
        """
        self.clear()
        self._stdscr.refresh()

        padding_yx = (1, 4)

        help_window = curses.newwin(self._parent_y, self._parent_x, 0, 0)
        help_window.attron(curses.A_BOLD)

        # display lines from __help__
        help_lines = \
            castero.__help__.split('\n')[:self._parent_y - padding_yx[0] - 1]
        help_lines.append("Press any key to exit this screen.")
        for i in range(len(help_lines)):
            help_window.addstr(i + padding_yx[0], padding_yx[1],
                               help_lines[i][:self._parent_x - padding_yx[1]])
        help_window.refresh()

        # simply wait until any key is pressed (temporarily disable timeout)
        self._stdscr.timeout(-1)
        self._stdscr.getch()
        self._stdscr.timeout(self.INPUT_TIMEOUT)

        self.clear()

    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.
        """
        # check if the screen size has changed
        self.update_parent_dimensions()

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

        footer_str += " -- Press %s for help" % self._config["key_help"]
        self._footer_window.attron(curses.A_BOLD)
        self._footer_window.addstr(
            1, 0, " " * (self._footer_window.getmaxyx()[1] - 1)
        )
        footer_str = footer_str[:self._footer_window.getmaxyx()[1] - 1]
        self._footer_window.addstr(1, 0, footer_str)

        # add window borders
        self._header_window.hline(1, 0,
                                  0, self._header_window.getmaxyx()[1])
        self._footer_window.hline(0, 0,
                                  0, self._footer_window.getmaxyx()[1])

        # update display for current perspective
        self._perspectives[self._active_perspective].display()

    def _get_active_perspective(self) -> Perspective:
        return self._perspectives[self._active_perspective]

    def _change_active_perspective(self, perspective_id) -> None:
        """Changes _active_perspective to the given perspective.

        Args:
            perspective_id: the ID of the perspective to change to
        """
        assert perspective_id in self._perspectives

        self._active_perspective = perspective_id
        self._perspectives[perspective_id].made_active()
        self.clear()

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

        curses.curs_set(1)
        self._stdscr.timeout(-1)  # disable timeouts while waiting for entry

        # display input prompt
        self._footer_window.addstr(
            1, 0, " " * (self._footer_window.getmaxyx()[1] - 1)
        )
        self._footer_window.addstr(1, 0, prompt)

        entry_pad = curses.newpad(1, 999)
        current_x = 0
        scroll_x = 0
        input_char = None
        while input_char not in [curses.KEY_ENTER, 10]:
            if input_char is not None:
                # manually handle backspace
                if input_char in [curses.KEY_BACKSPACE, 127]:
                    if current_x > 0:
                        entry_pad.delch(0, current_x - 1)
                        current_x -= 1
                        if scroll_x > 0:
                            scroll_x -= 1
                else:
                    # scroll the input pad if necessary
                    if current_x + len(prompt) > \
                            self._footer_window.getmaxyx()[1] - 1:
                        scroll_x += 1

                    # add the entered character to the pad
                    entry_pad.addch(0, current_x, input_char)
                    current_x += 1

                # display current portion of pad
                entry_pad.refresh(0, scroll_x,
                                  self._parent_y - 1, len(prompt),
                                  self._parent_y - 1,
                                  self._footer_window.getmaxyx()[1] - 1)

            # get the next input character
            input_char = self._footer_window.getch()

        self._stdscr.timeout(self.INPUT_TIMEOUT)
        self._footer_window.clear()
        curses.curs_set(0)

        return entry_pad.instr(0, 0, entry_pad.getmaxyx()[1]) \
            .decode('utf-8').strip()

    def _get_y_n(self, prompt) -> bool:
        """Prompts the user for a yes or no (y/n) input.

        Args:
            prompt: a string to inform the user of what they need to enter

        Returns:
            bool: true if the user presses y, false otherwise
        """
        assert self._footer_window is not None
        assert type(prompt) == str

        curses.echo()
        curses.curs_set(1)

        self._footer_window.addstr(
            1, 0, " " * (self._footer_window.getmaxyx()[1] - 1)
        )
        self._footer_window.addstr(1, 0, prompt)
        char = self._footer_window.getch()

        self._footer_window.clear()
        curses.curs_set(0)
        curses.noecho()

        return char == ord('y')

    def handle_input(self, c) -> bool:
        """Performs action corresponding to the user's input.

        Args:
            c: the input character

        Returns:
            bool: whether or not the application should continue running
        """
        for perspective_id in self._perspectives:
            if c == self.KEY_MAPPING[str(perspective_id)]:
                self._change_active_perspective(perspective_id)

        return self._get_active_perspective().handle_input(c)

    def add_feed(self) -> None:
        """Prompt the user for a feed and add it, if possible.
        """
        path = self._get_input_str("Enter the URL or path of the feed: ")
        try:
            # assume urls have http in them
            if "http" in path:
                feed = Feed(url=path)
            else:
                feed = Feed(file=path)
            if feed.validated:
                self._feeds[path] = feed
            self._feeds.write()
            self.create_menus()
            self.change_status("Feed '%s\' successfully added" % str(feed))
        except FeedError as e:
            if type(e) == FeedLoadError:
                self.change_status(
                    "Error: An error occurred while loading the file"
                )
            elif type(e) == FeedDownloadError:
                self.change_status(
                    "Error: An error occurred while downloading the feed"
                )
            elif type(e) == FeedParseError:
                self.change_status(
                    "Error: An error occurred while parsing the feed"
                )
            elif type(e) == FeedStructureError:
                self.change_status(
                    "Error: The provided feed is not a valid RSS document"
                )
            else:
                self.change_status(
                    "Error: An ambiguous error occurred while handling the"
                    " feed"
                )

    def delete_feed(self, index) -> None:
        """Deletes the feed at the given index.

        If the delete_feed_confirmation config option is true, this method will
        first ask for y/n confirmation before deleting the feed.

        Deleting a feed also deletes all downloaded/saved episodes.

        Args:
            index: the index of the feed to delete within self._feeds
        """
        should_delete = True
        if helpers.is_true(self._config["delete_feed_confirmation"]):
            should_delete = self._get_y_n(
                "Are you sure you want to delete this feed? (y/n): "
            )
        if should_delete:
            deleted = self._feeds.del_at(index, self._config)
            if deleted:
                self._feeds.write()
                self.create_menus()
                self.change_status("Feed successfully deleted")

    def reload_feeds(self) -> None:
        """Reloads the users' feeds.

        If the total number of feeds is >= the reload_feeds_threshold config
        option, this method will first ask for y/n confirmation.

        This method starts the reloading in a new un-managed thread.
        """
        should_reload = True
        if len(self._feeds) >= int(self._config["reload_feeds_threshold"]):
            should_reload = self._get_y_n(
                "Are you sure you want to reload all of your feeds?"
                " (y/n): "
            )
        if should_reload:
            t = threading.Thread(target=self._feeds.reload, args=[self])
            t.start()

    def save_episodes(self, feed_index, episode_index=None) -> None:
        """Saves the current selected feed or episode.

        If the user is saving an episode and the episode is already saved, this
        method will instead ask the user if they would like to delete the
        downloaded episode. However, if the user is saving a feed, there is no
        prompt to delete episodes, even if some are downloaded. In this case,
        downloaded episodes are simply skipped.

        Args:
            feed_index: the index of the feed to delete in self._feeds
            episode_index: (optional) the index of the episode to delete in the
            feed's episode list, if saving an individual episode
        """
        if episode_index is None:
            feed = self._feeds.at(feed_index)
            if feed is not None:
                for episode in feed.episodes:
                    if not episode.downloaded():
                        self._download_queue.add(episode)
        else:
            feed = self._feeds.at(feed_index)
            if feed is not None:
                episode = feed.episodes[episode_index]
                if episode.downloaded():
                    should_delete = self._get_y_n(
                        "Are you sure you want to delete the downloaded"
                        " episode? (y/n): ")
                    if should_delete:
                        episode.delete(self._config, self)
                else:
                    self._download_queue.add(episode)

    def clear(self) -> None:
        """Clear the screen.
        """
        self._stdscr.clear()

    def refresh(self) -> None:
        """Refresh the screen and all windows in all perspectives.
        """
        self._stdscr.refresh()

        for perspective_id in self._perspectives:
            self._perspectives[perspective_id].refresh()

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
        current_y, current_x = self._stdscr.getmaxyx()

        if current_y != self._parent_y or current_x != self._parent_x:
            self._parent_y, self._parent_x = current_y, current_x
            self._create_windows()
            self.create_menus()
            self.refresh()

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
        char = self._stdscr.getch()
        return char

    def change_status(self, status) -> None:
        """Changes the status message displayed in the footer.

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

        # check the status of any downloads
        self._download_queue.update()

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
                # status_timer should be reset during the next change_status()
                self._status = ""

    @property
    def parent_x(self) -> int:
        """int: the width of the parent screen, in characters"""
        return self._parent_x

    @property
    def parent_y(self) -> int:
        """int: the height of the parent screen, in characters"""
        return self._parent_y

    @property
    def config(self) -> Config:
        """Config: the user's config"""
        return self._config

    @property
    def feeds(self) -> Feeds:
        """Feeds: the user's feeds"""
        return self._feeds

    @property
    def perspectives(self) -> dict:
        """dict: the loaded Perspective's with id:perspective pairs"""
        return self._perspectives

    @property
    def queue(self) -> Queue:
        """Queue: the Queue of Player's"""
        return self._queue
