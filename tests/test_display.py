import curses
import os

import pytest

import castero
import castero.config as config
from castero.display import Display, DisplaySizeError
from castero.episode import Episode
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
                copyright="feed copyright",
                episodes=[])
    display._feeds["feed url"] = feed
    display.display()
    display._footer_window.attron.assert_called_with(curses.A_BOLD)
    display._footer_window.addstr.assert_called_with(
        1, 0,
        "Processed 1 feeds with 0 total episodes (avg. 0 episodes, med. 0)"
        " -- Press h for help"
    )


def test_display_display_borders(display):
    display.display()
    assert display._feed_window.hline.call_count == 1
    assert display._feed_window.vline.call_count == 1
    assert display._episode_window.hline.call_count == 1
    assert display._episode_window.vline.call_count == 1
    assert display._metadata_window.hline.call_count == 1
    assert display._header_window.hline.call_count == 1
    assert display._footer_window.hline.call_count == 1
    display._stdscr.reset_mock()


def test_display_help(display):
    display._stdscr.reset_mock()
    display._show_help()
    assert display._stdscr.refresh.call_count == 1
    assert display._stdscr.timeout.call_count == 2
    display._stdscr.timeout.assert_any_call(-1)
    display._stdscr.timeout.assert_any_call(Display.INPUT_TIMEOUT)


def test_display_refresh(display):
    display._stdscr.reset_mock()
    display.refresh()
    display._stdscr.refresh.assert_called_once()


def test_display_get_input_str(display):
    display._get_input_str("prompt")
    display._footer_window.clear.assert_called_once()
    assert display._footer_window.addstr.call_count == 2
    display._footer_window.addstr.assert_any_call(1, 0, "prompt")
    assert display._footer_window.called_with(1, len("prompt"))


def test_display_get_y_n(display):
    display._get_y_n("prompt")
    display._footer_window.clear.assert_called_once()
    assert display._footer_window.addstr.call_count == 2
    display._footer_window.addstr.assert_any_call(1, 0, "prompt")
    assert display._footer_window.called_with(1, len("prompt"))


def test_display_input_keys(display):
    myconfig = config.Config()
    ret_val = display.handle_input(ord('q'))
    assert not ret_val
    display._stdscr.reset_mock()

    ret_val = display.handle_input(ord('h'))
    assert ret_val
    display._stdscr.timeout.assert_any_call(-1)
    display._stdscr.reset_mock()

    movement_keys = [
        display.KEY_MAPPING[myconfig['key_up']],
        display.KEY_MAPPING[myconfig['key_right']],
        display.KEY_MAPPING[myconfig['key_down']],
        display.KEY_MAPPING[myconfig['key_left']],
        display.KEY_MAPPING[myconfig['key_scroll_up']],
        display.KEY_MAPPING[myconfig['key_scroll_down']],
    ]
    for key in movement_keys:
        display._metadata_updated = True
        ret_val = display.handle_input(key)
        assert ret_val
        assert not display._metadata_updated

    operation_keys = [
        display.KEY_MAPPING[myconfig['key_add_feed']],
        display.KEY_MAPPING[myconfig['key_delete']],
        display.KEY_MAPPING[myconfig['key_reload']],
        display.KEY_MAPPING[myconfig['key_save']],
        display.KEY_MAPPING[myconfig['key_play_selected']],
        display.KEY_MAPPING[myconfig['key_add_selected']],
        display.KEY_MAPPING[myconfig['key_clear']],
        display.KEY_MAPPING[myconfig['key_next']],
        display.KEY_MAPPING[myconfig['key_invert']],
        display.KEY_MAPPING[myconfig['key_pause_play']],
        display.KEY_MAPPING[myconfig['key_pause_play_alt']],
        display.KEY_MAPPING[myconfig['key_seek_forward']],
        display.KEY_MAPPING[myconfig['key_seek_forward_alt']],
        display.KEY_MAPPING[myconfig['key_seek_backward']],
        display.KEY_MAPPING[myconfig['key_seek_backward_alt']],
    ]
    for key in operation_keys:
        ret_val = display.handle_input(key)
        assert ret_val


def test_display_draw_metadata(display):
    feed = Feed(url="feed url",
                title="feed title",
                description="feed description",
                link="feed link",
                last_build_date="feed last_build_date",
                copyright="feed copyright",
                episodes=[])
    episode = Episode(feed,
                      title="episode title",
                      description="episode description",
                      link="episode link",
                      pubdate="episode pubdate",
                      copyright="episode copyright",
                      enclosure="episode enclosure")
    feed.episodes.append(episode)
    display._feeds["feed url"] = feed
    display._active_window = 0
    display._draw_metadata()
    display._active_window = 1
    display._draw_metadata()


def test_display_getch(display):
    display._stdscr.reset_mock()
    display.getch()
    display._stdscr.getch.assert_called_once()


def test_display_get_active_window(display):
    display._active_window = 0
    assert display.get_active_window() == display._feed_window
    display._active_window = 1
    assert display.get_active_window() == display._episode_window
    display._active_window = 2
    assert display.get_active_window() == display._metadata_window


def test_display_get_active_menu(display):
    display._active_window = 0
    assert display.get_active_menu() == display._feed_menu
    display._active_window = 1
    assert display.get_active_menu() == display._episode_menu


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


def test_display_create_player(display):
    feed = Feed(url="feed url",
                title="feed title",
                description="feed description",
                link="feed link",
                last_build_date="feed last_build_date",
                copyright="feed copyright",
                episodes=[])
    episode = Episode(feed,
                      title="episode title",
                      description="episode description",
                      link="episode link",
                      pubdate="episode pubdate",
                      copyright="episode copyright",
                      enclosure="episode enclosure")
    feed.episodes.append(episode)
    feed.episodes.append(episode)
    feed.episodes.append(episode)
    display._feeds["feed url"] = feed
    display._active_window = 0
    display._create_player_from_selected()
    assert display._queue.length == 3
    display._queue.clear()
    assert display._queue.length == 0
    display._active_window = 1
    display._create_player_from_selected()
    assert display._queue.length == 1


def test_display_nonempty(display):
    myfeed = Feed(file=my_dir + "/feeds/valid_enclosures.xml")
    display._feeds[myfeed._file] = myfeed
    display.create_menus()
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
    feed_dir = my_dir + "/feeds/valid_enclosures.xml"
    display._footer_window.set_test_input(feed_dir)
    display._add_feed()
    assert len(display._feeds) == 1
    assert type(display._feeds[feed_dir]) == Feed


def test_display_add_feed_errors(display):
    test_inputs = ["fake", "http://fake", my_dir + "/feeds/broken_is_rss.xml",
                   my_dir + "/datafiles/parse_error.conf"]
    for test_input in test_inputs:
        display._footer_window.set_test_input(test_input)
        display._add_feed()
        assert display._status.startswith("Error:")
        display._status = ""
        assert len(display._feeds) == 0


def test_display_delete_feed(display):
    feed = Feed(url="feed url",
                title="feed title",
                description="feed description",
                link="feed link",
                last_build_date="feed last_build_date",
                copyright="feed copyright",
                episodes=[])
    display._feeds["feed url"] = feed
    assert len(display._feeds) == 1
    display._delete_feed()
    assert len(display._feeds) == 0
