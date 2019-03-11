import os
from unittest import mock

from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def get_primary_perspective(display):
    """Retrieve the Primary perspective.

    Args:
        display: the display containing the loaded perspective

    Returns:
        Primary: the loaded Primary perspective
    """
    return display.perspectives[1]


def test_perspective_primary_borders(display):
    perspective = get_primary_perspective(display)

    display.display()
    assert perspective._feed_window.hline.call_count == 1
    assert perspective._feed_window.vline.call_count == 1
    assert perspective._episode_window.hline.call_count == 1
    assert perspective._episode_window.vline.call_count == 1
    assert perspective._metadata_window.hline.call_count == 1
    display._stdscr.reset_mock()


def test_perspective_primary_display_feed_metadata(display):
    perspective = get_primary_perspective(display)
    perspective._active_window = 0

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.feeds["feed url"] = feed

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window)
    display._stdscr.reset_mock()


def test_perspective_primary_display_episode_metadata(display):
    perspective = get_primary_perspective(display)
    perspective._active_window = 1

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.feeds["feed url"] = feed

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window)
    display._stdscr.reset_mock()


def test_perspective_primary_input_keys(display):
    perspective = get_primary_perspective(display)

    display._footer_window.getch = mock.MagicMock(return_value=10)

    ret_val = perspective.handle_input(ord('q'))
    assert not ret_val
    display._stdscr.reset_mock()

    ret_val = perspective.handle_input(ord('h'))
    assert ret_val
    display._stdscr.timeout.assert_any_call(-1)
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
        display.KEY_MAPPING[Config['key_add_feed']],
        display.KEY_MAPPING[Config['key_delete']],
        display.KEY_MAPPING[Config['key_reload']],
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
    ]
    for key in operation_keys:
        ret_val = perspective.handle_input(key)
        assert ret_val


def test_perspective_primary_draw_metadata(display):
    perspective = get_primary_perspective(display)

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
    display.feeds["feed url"] = feed
    perspective._draw_metadata(perspective._metadata_window)
    perspective._draw_metadata(perspective._metadata_window)


def test_perspective_primary_get_active_menu(display):
    perspective = get_primary_perspective(display)

    perspective._active_window = 0
    assert perspective._get_active_menu() == perspective._feed_menu
    perspective._active_window = 1
    assert perspective._get_active_menu() == perspective._episode_menu


def test_perspective_primary_create_player(display):
    perspective = get_primary_perspective(display)

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
    display.feeds["feed url"] = feed
    perspective._active_window = 0
    perspective._create_player_from_selected()
    assert display.queue.length == 3
    display.queue.clear()
    assert display.queue.length == 0
    perspective._active_window = 1
    perspective._create_player_from_selected()
    assert display.queue.length == 1


def test_perspective_regression_11(display):
    perspective = get_primary_perspective(display)

    old_ddir = Config["custom_download_dir"]
    Config.data["custom_download_dir"] = os.path.join(my_dir, "downloaded")

    feed = Feed(file="%s/feeds/valid_enclosures.xml" % (my_dir))
    display.feeds["feed url"] = feed
    display.queue.clear()
    perspective._active_window = 1
    perspective._create_player_from_selected()

    assert display.queue[0]._path == os.path.join(my_dir, "downloaded",
                                                  "myfeed_title",
                                                  "myfeed_item1_title.mp3")

    Config.data["custom_download_dir"] = old_ddir


def test_perspective_primary_invert_episodes(display):
    perspective = get_primary_perspective(display)
    perspective._active_window = 1

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.feeds["feed url"] = feed

    display.feeds.at(0).invert_episodes = mock.MagicMock()
    perspective._invert_selected_menu()
    display.feeds.at(0).invert_episodes.assert_called_once()
    display._stdscr.reset_mock()
