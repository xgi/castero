import curses
import os
from unittest import mock

import pytest

import castero
from castero.display import Display, DisplaySizeError
from castero.feed import Feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def test_display_init(display):
    assert isinstance(display, Display)
    display._stdscr.reset_mock()


def test_display_display_header(display):
    display.display()
    display._header_window.attron.assert_called_with(curses.A_BOLD)
    display._header_window.addstr.assert_called_with(0, 0, castero.__title__)
    display._stdscr.reset_mock()


def test_display_display_footer_empty(display):
    display.display()
    display._footer_window.attron.assert_called_with(curses.A_BOLD)
    display._footer_window.addstr.assert_called_with(
        1, 0, "No feeds added -- Press h for help"
    )
    display._stdscr.reset_mock()
    feed = Feed(url="feed url",
                title="feed title",
                description="feed description",
                link="feed link",
                last_build_date="feed last_build_date",
                copyright="feed copyright")
    display.database.feeds = mock.MagicMock(return_value=[feed])
    display.display()
    display._footer_window.attron.assert_called_with(curses.A_BOLD)
    display._footer_window.addstr.assert_called_with(
        1, 0,
        "Found 1 feeds with 0 total episodes (avg. 0 episodes, med. 0)"
        " -- Press h for help"
    )


def test_display_display_borders(display):
    display.display()
    assert display._header_window.hline.call_count == 1
    assert display._footer_window.hline.call_count == 1
    display._stdscr.reset_mock()


def test_display_help(display):
    display._stdscr.reset_mock()
    display.show_help()
    assert display._stdscr.refresh.call_count == 1
    assert display._stdscr.timeout.call_count == 2
    display._stdscr.timeout.assert_any_call(-1)
    display._stdscr.timeout.assert_any_call(Display.INPUT_TIMEOUT)


def test_display_refresh(display):
    display._stdscr.reset_mock()
    display.refresh()
    assert display._stdscr.refresh.call_count == 1


def test_display_get_input_str(display):
    display._footer_window.getch = mock.Mock()
    display._footer_window.getch.side_effect = [ord('a'), ord('b'), 10]
    display._get_input_str("prompt")
    assert display._footer_window.getch.call_count == 3
    assert display._footer_window.clear.call_count == 1
    assert display._footer_window.addstr.call_count == 2
    display._footer_window.addstr.assert_any_call(1, 0, "prompt")
    assert display._footer_window.called_with(1, len("prompt"))


def test_display_get_y_n(display):
    display._get_y_n("prompt")
    assert display._footer_window.clear.call_count == 1
    assert display._footer_window.addstr.call_count == 2
    display._footer_window.addstr.assert_any_call(1, 0, "prompt")
    assert display._footer_window.called_with(1, len("prompt"))


def test_display_input_keys(display):
    for perspective_id in display.perspectives:
        perspective = display.perspectives[perspective_id]
        perspective.handle_input = mock.MagicMock()
        display.handle_input(display.KEY_MAPPING[str(perspective_id)])
        assert perspective.handle_input.call_count == 1


def test_display_getch(display):
    display._stdscr.reset_mock()
    display.getch()
    assert display._stdscr.getch.call_count == 1


def test_display_update_status(display):
    display._status = ""
    display._status_timer = 0
    display.change_status("test status")
    assert display._status == "test status"
    assert display._status_timer == display.STATUS_TIMEOUT


def test_display_update(display):
    display._status = "test status"
    display._status_timer = 1
    display.update()
    assert display._status_timer == 0
    assert display._status == ""


def test_display_nonempty(display):
    myfeed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.database.feeds = mock.MagicMock(return_value=[myfeed])
    display.menus_valid = False
    display.display()


def test_display_min_dimensions(display):
    display.display()
    display._stdscr.setmaxyx(100, Display.MIN_WIDTH - 1)
    with pytest.raises(DisplaySizeError):
        display.display()
    display._stdscr.setmaxyx(Display.MIN_HEIGHT - 1, 100)
    with pytest.raises(DisplaySizeError):
        display.display()


def test_display_add_feed(display):
    feed_dir = my_dir + "/feeds/valid_basic.xml"
    display._get_input_str = mock.MagicMock(return_value=feed_dir)
    display.add_feed()
    assert len(display.database.feeds()) == 1


def test_display_add_feed_errors(display):
    test_inputs = ["fake", "http://fake", my_dir + "/feeds/broken_is_rss.xml",
                   my_dir + "/datafiles/parse_error.conf"]
    for test_input in test_inputs:
        display._get_input_str = mock.MagicMock(return_value=test_input)
        display.add_feed()
        assert "Error" in display._status
        display._status = ""
        assert len(display.database.feeds()) == 0


def test_display_delete_feed(display):
    feed = Feed(url="feed url",
                title="feed title",
                description="feed description",
                link="feed link",
                last_build_date="feed last_build_date",
                copyright="feed copyright",
                episodes=[])
    display.database.replace_feed(feed)
    assert len(display.database.feeds()) == 1
    display.delete_feed(feed)
    assert len(display.database.feeds()) == 0
