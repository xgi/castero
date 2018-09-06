from abc import ABC, abstractmethod

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
