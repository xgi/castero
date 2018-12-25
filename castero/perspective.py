import curses
from abc import ABC, abstractmethod

import cjkwrap

from castero.menu import Menu


class Perspective(ABC):
    """The Perspective class.

    This class is extended by perspectives -- classes which offer methods to
    handle display elements with a certain layout. Perspectives only control
    the "inside" elements of the display: the header and footer are controlled
    by the display class.

    The user is able to switch between perspectives by using the 0-9 keys
    corresponding to the perspective's ID.

    Instances of this class do not generally hold data variables, i.e. the
    instance of the Feed class or Config class. We instead reference the
    variables held in Display instance.
    """
    ID = -1

    @abstractmethod
    def __init__(self, display):
        """Initializes the object.

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

        Creates the following windows:
            - _feed_window, _episode_window, _metadata_window
        Each window is set to use the default color pair (1), and each window
        takes up one-third of the display.
        """

    @abstractmethod
    def create_menus(self) -> None:
        """Create the menus used in each window, if necessary.

        Windows which have menus should be created prior to running this method
        (using _create_windows).

        If the menus already exist when this method is run, this method will
        delete them and create new ones.
        """

    @abstractmethod
    def display(self) -> None:
        """Draws all windows and sub-features, including titles and borders.
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
    def _get_active_menu(self) -> Menu:
        """Retrieve the active Menu, if there is one.

        Returns:
            Menu: the active Menu, or None
        """

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

    def _draw_metadata(self, window, feed=None, episode=None) -> None:
        """Draws the metadata of the selected feed/episode onto the window.

        Exactly one of feed or episode must be specified.

        Args:
            window: the curses window which will display the metadata
            feed: (optional) the Feed whose metadata will be displayed
            episode: (optional) the Episode whose metadata will be displayed
        """
        assert window is not None
        assert feed != episode and (feed is None or episode is None)

        output_lines = []  # 2D array, each element is [attr, str]
        max_lines = window.getmaxyx()[0] - 2
        max_line_width = window.getmaxyx()[1] - 1

        # clear the window by drawing blank lines
        for y in range(2, window.getmaxyx()[0]):
            window.addstr(y, 0, " " * max_line_width)

        if feed is not None:
            # draw feed title
            self._append_metadata_lines(window, feed.title, output_lines,
                                        attr=curses.A_BOLD)
            # draw feed lastBuildDate
            self._append_metadata_lines(window, feed.last_build_date,
                                        output_lines,
                                        add_blank=True)
            # draw feed link
            self._append_metadata_lines(window, feed.link, output_lines,
                                        add_blank=True)
            # draw feed description
            self._append_metadata_lines(window, "Description:", output_lines,
                                        attr=curses.A_BOLD)
            self._append_metadata_lines(window, feed.description, output_lines,
                                        add_blank=True)
            # draw feed copyright
            self._append_metadata_lines(window, "Copyright:", output_lines,
                                        attr=curses.A_BOLD)
            self._append_metadata_lines(window, feed.copyright, output_lines,
                                        add_blank=True)
            # draw feed number of episodes
            num_dl = sum([episode.downloaded(self._display.config) for
                          episode in feed.episodes])
            self._append_metadata_lines(window, "Episodes:", output_lines,
                                        attr=curses.A_BOLD)
            self._append_metadata_lines(window,
                                        "Found %d episodes (%d downloaded)" % (
                                            len(feed.episodes), num_dl
                                        ), output_lines
                                        )
        elif episode is not None:
            # draw episode title
            self._append_metadata_lines(window, episode.title, output_lines,
                                        attr=curses.A_BOLD)
            # draw episode pubdate
            self._append_metadata_lines(window, episode.pubdate, output_lines,
                                        add_blank=True)
            # draw episode link
            self._append_metadata_lines(window, episode.link, output_lines,
                                        add_blank=True)
            # draw episode description
            self._append_metadata_lines(window, "Description:", output_lines,
                                        attr=curses.A_BOLD)
            self._append_metadata_lines(window, episode.description,
                                        output_lines,
                                        add_blank=True)
            # draw episode copyright
            self._append_metadata_lines(window, "Copyright:", output_lines,
                                        attr=curses.A_BOLD)
            self._append_metadata_lines(window, episode.copyright,
                                        output_lines,
                                        add_blank=True)

            # draw episode downloaded
            self._append_metadata_lines(window, "Downloaded:", output_lines,
                                        attr=curses.A_BOLD)
            self._append_metadata_lines(window,
                                        "Episode downloaded and available for"
                                        " offline playback." if
                                        episode.downloaded(
                                            self._display.config) else
                                        "Episode not downloaded.",
                                        output_lines)

        y = 2
        for line in output_lines[:max_lines]:
            window.attrset(curses.color_pair(1))
            if line[0] != -1:
                window.attron(line[0])
            window.addstr(y, 0, line[1])
            y += 1 + line[1].count('\n')

    def _append_metadata_lines(self, window, string, output_lines, attr=-1,
                               add_blank=False) -> None:
        """Appends properly formatted lines to the 2D output_lines array.

        Args:
            window: the curses window which will display the metadata
            string: the string to add to output_lines
            output_lines: 2D array, each element is [attr, str]
            attr: (optional) the attribute (i.e. curses.A_BOLD)
        """
        max_lines = int(0.7 * window.getmaxyx()[0])
        max_line_width = window.getmaxyx()[1] - 1
        lines = cjkwrap.wrap(string, max_line_width)

        # truncate to at most 70% of the total lines on the screen
        lines = lines[:max_lines]

        # add all lines to array
        for line in lines:
            output_lines.append([attr, line])

        # add a blank line afterward, if necessary
        if add_blank:
            output_lines.append([-1, ""])
