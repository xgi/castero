import curses
import os
from unittest import mock

import pytest

from castero.datafile import DataFile
from castero.display import Display
from castero.database import Database


class Helpers:
    """The Helpers class.

    Provides functions that are useful to multiple test units.

    This class should not be instantiated.
    """

    @staticmethod
    def hide_user_database():
        """Moves the user's database files to make them unreachable.
        """
        DataFile.ensure_path(Database.PATH)
        DataFile.ensure_path(Database.OLD_PATH)
        if os.path.exists(Database.PATH):
            os.rename(Database.PATH, Database.PATH + ".tmp")
        if os.path.exists(Database.OLD_PATH):
            os.rename(Database.OLD_PATH, Database.OLD_PATH + ".tmp")

    @staticmethod
    def restore_user_database():
        """Restores the user's database files if they have been hidden."""
        DataFile.ensure_path(Database.PATH)
        DataFile.ensure_path(Database.OLD_PATH)
        if os.path.exists(Database.PATH + ".tmp"):
            os.rename(Database.PATH + ".tmp", Database.PATH)
        if os.path.exists(Database.OLD_PATH + ".tmp"):
            os.rename(Database.OLD_PATH + ".tmp", Database.OLD_PATH)


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
            mock.patch('curses.newpad'), \
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
    Helpers.hide_user_database()
    yield
    Helpers.restore_user_database()


@pytest.yield_fixture()
def display(prevent_modification, stdscr):
    database = Database()
    yield Display(stdscr, database)
