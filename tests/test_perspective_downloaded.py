import os
from unittest import mock

from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def get_downloaded_perspective(display):
    """Retrieve the Downloaded perspective.

    Args:
        display: the display containing the loaded perspective

    Returns:
        Downloaded: the loaded Downloaded perspective
    """
    display._active_perspective = 4
    return display.perspectives[4]


def test_perspective_downloaded_borders(display):
    perspective = get_downloaded_perspective(display)

    display.display()
    assert perspective._downloaded_window.hline.call_count == 1
    assert perspective._downloaded_window.vline.call_count == 1
    assert perspective._metadata_window.hline.call_count == 1
    display._stdscr.reset_mock()


def test_perspective_downloaded_display_feed_metadata(display):
    perspective = get_downloaded_perspective(display)
    perspective._active_window = 0

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.database.replace_feed(feed)

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window)
    display._stdscr.reset_mock()


def test_perspective_downloaded_display_episode_metadata(display):
    perspective = get_downloaded_perspective(display)
    perspective._active_window = 1

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.database.replace_feed(feed)

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window)
    display._stdscr.reset_mock()


def test_perspective_downloaded_input_keys(display):
    perspective = get_downloaded_perspective(display)

    display._footer_window.getch = mock.MagicMock(return_value=10)

    ret_val = perspective.handle_input(ord('q'))
    assert not ret_val
    display._stdscr.reset_mock()

    ret_val = perspective.handle_input(ord('h'))
    assert ret_val
    display._stdscr.reset_mock()

    movement_keys = [
        display.KEY_MAPPING[Config['key_up']],
        display.KEY_MAPPING[Config['key_right']],
        display.KEY_MAPPING[Config['key_down']],
        display.KEY_MAPPING[Config['key_left']],
        display.KEY_MAPPING[Config['key_scroll_up']],
        display.KEY_MAPPING[Config['key_scroll_down']],
    ]
    for key in movement_keys:
        perspective._metadata_updated = True
        ret_val = perspective.handle_input(key)
        assert ret_val
        assert not perspective._metadata_updated

    operation_keys = [
        display.KEY_MAPPING[Config['key_delete']],
        display.KEY_MAPPING[Config['key_reload']],
        display.KEY_MAPPING[Config['key_reload_selected']],
        display.KEY_MAPPING[Config['key_save']],
        display.KEY_MAPPING[Config['key_play_selected']],
        display.KEY_MAPPING[Config['key_add_selected']],
        display.KEY_MAPPING[Config['key_clear']],
        display.KEY_MAPPING[Config['key_next']],
        display.KEY_MAPPING[Config['key_invert']],
        display.KEY_MAPPING[Config['key_pause_play']],
        display.KEY_MAPPING[Config['key_pause_play_alt']],
        display.KEY_MAPPING[Config['key_seek_forward']],
        display.KEY_MAPPING[Config['key_seek_forward_alt']],
        display.KEY_MAPPING[Config['key_seek_backward']],
        display.KEY_MAPPING[Config['key_seek_backward_alt']],
        display.KEY_MAPPING[Config['key_mark_played']],
        display.KEY_MAPPING[Config['key_rate_increase']],
        display.KEY_MAPPING[Config['key_rate_decrease']],
        display.KEY_MAPPING[Config['key_show_url']],
        display.KEY_MAPPING[Config['key_execute']]
    ]
    for key in operation_keys:
        display._active_window = 0
        assert perspective.handle_input(key)


def test_perspective_downloaded_draw_metadata(display):
    perspective = get_downloaded_perspective(display)

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
    display.database.replace_feed(feed)
    display.database.replace_episode(feed, episode)
    perspective._draw_metadata(perspective._metadata_window)
    perspective._draw_metadata(perspective._metadata_window)


def test_perspective_downloaded_get_active_menu(display):
    perspective = get_downloaded_perspective(display)

    perspective._active_window = 0
    assert perspective._get_active_menu() == perspective._downloaded_menu


def test_perspective_downloaded_invert_episodes(display):
    perspective = get_downloaded_perspective(display)

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.database.replace_feed(feed)
    display.database.replace_episodes(feed, feed.parse_episodes())
    display.menus_valid = False

    perspective._downloaded_menu.invert = mock.MagicMock()

    perspective._active_window = 0
    perspective._invert_selected_menu()
    assert perspective._downloaded_menu.invert.call_count == 1
    display._stdscr.reset_mock()
