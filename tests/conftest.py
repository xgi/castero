import os
import pytest
import curses
from shutil import copyfile
from unittest import mock
from castero.display import Display
from castero.config import Config
from castero.feeds import Feeds


class Helpers:
    """The Helpers class.

    Provides functions that are useful to multiple test units.

    This class should not be instantiated.
    """
    @staticmethod
    def hide_user_feeds():
        """Moves the user's feeds file, if it exists, to make it unreachable.
        """
        if os.path.exists(Feeds.PATH):
            os.rename(Feeds.PATH, Feeds.PATH + ".tmp")
        copyfile(Feeds.DEFAULT_PATH, Feeds.PATH)

    @staticmethod
    def restore_user_feeds():
        """Restores the user's feeds file if it has been hidden."""
        if os.path.exists(Feeds.PATH + ".tmp"):
            os.rename(Feeds.PATH + ".tmp", Feeds.PATH)

    @staticmethod
    def hide_user_config():
        """Moves the user's config file, if it exists, to make it unreachable.
        """
        if os.path.exists(Config.PATH):
            os.rename(Config.PATH, Config.PATH + ".tmp")
        copyfile(Config.DEFAULT_PATH, Config.PATH)

    @staticmethod
    def restore_user_config():
        """Restores the user's config file if it has been hidden."""
        if os.path.exists(Config.PATH + ".tmp"):
            os.rename(Config.PATH + ".tmp", Config.PATH)


class MockStdscr(mock.MagicMock):
    """The MockStdscr class.

    Provides functions to mock typical stdscr behavior.
    """
    def getstr(self, start, end):
        return self.test_input.encode('utf-8')

    def setmaxyx(self, nlines, ncols):
        self.nlines, self.ncols = nlines, ncols

    def getmaxyx(self):
        return self.nlines, self.ncols

    def derwin(self, nlines, ncols, x, y):
        return MockStdscr(nlines=nlines, ncols=ncols,
                          x=x, y=y,
                          test_input='unspecified test input')

    def set_test_input(self, str):
        self.test_input = str


@pytest.yield_fixture()
def stdscr():
    with mock.patch('curses.initscr'), \
         mock.patch('curses.echo'), \
         mock.patch('curses.flash'), \
         mock.patch('curses.endwin'), \
         mock.patch('curses.newwin'), \
         mock.patch('curses.noecho'), \
         mock.patch('curses.cbreak'), \
         mock.patch('curses.doupdate'), \
         mock.patch('curses.nocbreak'), \
         mock.patch('curses.curs_set'), \
         mock.patch('curses.init_pair'), \
         mock.patch('curses.color_pair'), \
         mock.patch('curses.has_colors'), \
         mock.patch('curses.start_color'), \
         mock.patch('curses.use_default_colors'):
        result = MockStdscr(nlines=24, ncols=100, x=0, y=0)
        curses.initscr.return_value = result
        curses.newwin.side_effect = lambda *args: result.derwin(*args)
        curses.color_pair.return_value = 1
        curses.has_colors.return_value = True
        curses.ACS_VLINE = 0
        curses.ACS_HLINE = 0
        curses.COLORS = 16
        curses.COLOR_PAIRS = 16
        yield result


@pytest.yield_fixture()
def prevent_modification():
    Helpers.hide_user_feeds()
    Helpers.hide_user_config()
    yield
    Helpers.restore_user_feeds()
    Helpers.restore_user_config()


@pytest.yield_fixture()
def display(prevent_modification, stdscr):
    config = Config()
    feeds = Feeds()
    yield Display(stdscr, config, feeds)