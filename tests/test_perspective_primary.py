import os
from unittest import mock

from castero.config import Config
from castero.episode import Episode
from castero.feed import Feed

my_dir = os.path.dirname(os.path.realpath(__file__))


def get_primary_perspective(display):
    """Retrieve the Primary perspective.

    :param display the display containing the loaded perspective
    :returns Primary: the loaded Primary perspective
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
    display.database.replace_feed(feed)

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window)
    display._stdscr.reset_mock()


def test_perspective_primary_display_episode_metadata(display):
    perspective = get_primary_perspective(display)
    perspective._active_window = 1

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.database.replace_feed(feed)

    perspective._draw_metadata = mock.MagicMock()
    display.display()
    perspective._draw_metadata.assert_called_with(perspective._metadata_window)
    display._stdscr.reset_mock()


def test_perspective_primary_input_keys(display):
    perspective = get_primary_perspective(display)

    display._get_input_str = mock.Mock(return_value="")
    display._footer_window.getch = mock.MagicMock(return_value=10)

    ret_val = perspective.handle_input(ord("h"))
    assert ret_val
    display._stdscr.reset_mock()

    movement_keys = [
        display.KEY_MAPPING[Config["key_up"]],
        display.KEY_MAPPING[Config["key_right"]],
        display.KEY_MAPPING[Config["key_down"]],
        display.KEY_MAPPING[Config["key_left"]],
        display.KEY_MAPPING[Config["key_scroll_up"]],
        display.KEY_MAPPING[Config["key_scroll_down"]],
    ]
    for key in movement_keys:
        perspective._metadata_updated = True
        ret_val = perspective.handle_input(key)
        assert ret_val
        assert not perspective._metadata_updated

    operation_keys = [
        display.KEY_MAPPING[Config["key_add_feed"]],
        display.KEY_MAPPING[Config["key_delete"]],
        display.KEY_MAPPING[Config["key_remove"]],
        display.KEY_MAPPING[Config["key_reload"]],
        display.KEY_MAPPING[Config["key_reload_selected"]],
        display.KEY_MAPPING[Config["key_save"]],
        display.KEY_MAPPING[Config["key_play_selected"]],
        display.KEY_MAPPING[Config["key_add_selected"]],
        display.KEY_MAPPING[Config["key_clear"]],
        display.KEY_MAPPING[Config["key_next"]],
        display.KEY_MAPPING[Config["key_invert"]],
        display.KEY_MAPPING[Config["key_pause_play"]],
        display.KEY_MAPPING[Config["key_pause_play_alt"]],
        display.KEY_MAPPING[Config["key_seek_forward"]],
        display.KEY_MAPPING[Config["key_seek_forward_alt"]],
        display.KEY_MAPPING[Config["key_seek_backward"]],
        display.KEY_MAPPING[Config["key_seek_backward_alt"]],
        display.KEY_MAPPING[Config["key_mark_played"]],
        display.KEY_MAPPING[Config["key_execute"]],
    ]
    for key in operation_keys:
        display._active_window = 0
        assert perspective.handle_input(key)
        display._active_window = 1
        assert perspective.handle_input(key)

    ret_val = perspective.handle_input(ord("q"))
    assert not ret_val
    display._stdscr.reset_mock()


def test_perspective_primary_draw_metadata(display):
    perspective = get_primary_perspective(display)

    feed = Feed(
        url="feed url",
        title="feed title",
        description="feed description",
        link="feed link",
        last_build_date="feed last_build_date",
        copyright="feed copyright",
        episodes=[],
    )
    episode = Episode(
        feed,
        title="episode title",
        description="episode description",
        link="episode link",
        pubdate="episode pubdate",
        copyright="episode copyright",
        enclosure="episode enclosure",
    )
    display.database.replace_feed(feed)
    display.database.replace_episode(feed, episode)
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

    feed = Feed(
        url="feed url",
        title="feed title",
        description="feed description",
        link="feed link",
        last_build_date="feed last_build_date",
        copyright="feed copyright",
        episodes=[],
    )
    episode1 = Episode(
        feed,
        title="episode1 title",
        description="episode1 description",
        link="episode1 link",
        pubdate="episode1 pubdate",
        copyright="episode1 copyright",
        enclosure="episode1 enclosure",
    )
    episode2 = Episode(
        feed,
        title="episode2 title",
        description="episode2 description",
        link="episode2 link",
        pubdate="episode2 pubdate",
        copyright="episode2 copyright",
        enclosure="episode2 enclosure",
    )
    display.display()
    display.database.replace_feed(feed)
    display.database.replace_episodes(feed, [episode1, episode2])
    perspective._feed_menu.update_items(None)
    perspective._episode_menu.update_items(feed)
    perspective._active_window = 0
    perspective._create_player_from_selected()
    assert display.queue.length == 2
    display.queue.clear()
    assert display.queue.length == 0
    perspective._active_window = 1
    perspective._create_player_from_selected()
    assert display.queue.length == 1


def test_perspective_primary_queue_unplayed(display):
    perspective = get_primary_perspective(display)

    feed = Feed(
        url="feed url",
        title="feed title",
        description="feed description",
        link="feed link",
        last_build_date="feed last_build_date",
        copyright="feed copyright",
        episodes=[],
    )
    episode1 = Episode(
        feed,
        title="episode1 title",
        description="episode1 description",
        link="episode1 link",
        pubdate="episode1 pubdate",
        copyright="episode1 copyright",
        enclosure="episode1 enclosure",
        played=True,
    )
    episode2 = Episode(
        feed,
        title="episode2 title",
        description="episode2 description",
        link="episode2 link",
        pubdate="episode2 pubdate",
        copyright="episode2 copyright",
        enclosure="episode2 enclosure",
    )
    display.display()
    display.database.replace_feed(feed)
    display.database.replace_episodes(feed, [episode1, episode2])
    perspective._feed_menu.update_items(None)
    perspective._episode_menu.update_items(feed)
    perspective._active_window = 0
    perspective._queue_unplayed_feed_episodes = False
    perspective._create_player_from_selected()
    assert display.queue.length == 2
    display.queue.clear()
    perspective._queue_unplayed_feed_episodes = True
    perspective._create_player_from_selected()
    assert display.queue.length == 1


def test_perspective_primary_invert_episodes(display):
    perspective = get_primary_perspective(display)

    feed = Feed(file=my_dir + "/feeds/valid_basic.xml")
    display.database.replace_feed(feed)
    display.database.replace_episodes(feed, feed.parse_episodes())
    display.menus_valid = False

    perspective._feed_menu.invert = mock.MagicMock()
    perspective._episode_menu.invert = mock.MagicMock()

    perspective._active_window = 0
    perspective._invert_selected_menu()
    assert perspective._feed_menu.invert.call_count == 1
    perspective._active_window = 1
    perspective._invert_selected_menu()
    assert perspective._episode_menu.invert.call_count == 1
    display._stdscr.reset_mock()
