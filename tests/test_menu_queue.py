from unittest import mock

from castero.episode import Episode
from castero.player import Player
from castero.queue import Queue
from castero.feed import Feed
from castero.menus.queuemenu import QueueMenu

feed = mock.MagicMock(spec=Feed)
player1 = mock.MagicMock(spec=Player)
player2 = mock.MagicMock(spec=Player)
player1.episode = mock.MagicMock(spec=Episode)
window = mock.MagicMock()
window.getmaxyx = mock.MagicMock(return_value=(40, 80))
source = mock.MagicMock(spec=Queue)
source.__iter__.return_value = [player1, player2]
source.__getitem__.return_value = player1


def test_menu_queue_init():
    mymenu = QueueMenu(window, source)
    assert isinstance(mymenu, QueueMenu)


def test_menu_queue_update_items():
    mymenu = QueueMenu(window, source)
    mymenu.update_items(None)
    assert len(mymenu._items()) == 2


@mock.patch('curses.A_NORMAL')
def test_menu_queue_items(mock_A_NORMAL):
    mymenu = QueueMenu(window, source)
    mymenu.update_items(feed)
    items = mymenu._items()
    assert {
        'attr': mock_A_NORMAL,
        'tags': [],
        'text': str(player1)
    } in items


def test_menu_queue_item_none():
    mymenu = QueueMenu(window, source)
    assert mymenu.item() == source.__getitem__()


def test_menu_queue_metadata():
    mymenu = QueueMenu(window, source)
    mymenu.update_items(feed)
    assert mymenu.metadata() == player1.episode.metadata


def test_menu_queue_update_child():
    mymenu = QueueMenu(window, source)
    mymenu.update_items(feed)
    items = mymenu._items()
    mymenu.update_child()
    assert mymenu._items() == items
