import pytest
import curses
from unittest import mock
from castero.display import Display
from castero.config import Config
from castero.feeds import Feeds
from tests import test_config, test_feeds


class MockStdscr(mock.MagicMock):
    """The MockStdscr class.

    Provides functions to mock typical stdscr behavior.
    """
    def getyx(self):
        return self.x, self.y

    def getmaxyx(self):
        return self.nlines, self.ncols

    def derwin(self, nlines, ncols, x, y):
        return MockStdscr(nlines=nlines, ncols=ncols, x=x, y=y)


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
        result = MockStdscr(nlines=24, ncols=80, x=0, y=0)
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
def display(stdscr):
    test_config.hide_user_config()
    test_feeds.hide_user_feeds()
    config = Config()
    feeds = Feeds()
    test_config.restore_user_config()
    test_feeds.restore_user_feeds()
    return Display(stdscr, config, feeds)
