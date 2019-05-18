__title__ = "castero"
__description__ = "A TUI podcast client for the terminal"
__keywords__ = "podcast commandline terminal tui curses"
__author__ = "Jake Robertson"
__author_email__ = "jake@faltro.com"
__version__ = "0.5.5"
__date__ = "2019-05-18"
__copyright__ = "Copyright (c) 2018 Jake Robertson"
__license__ = "MIT License"
__url__ = "https://github.com/xgi/castero"

__help__ = """\
%s help
============

Version: %s
Updated: %s
Maintainer: %s <%s>
License: %s
URL: %s

Commands
    {key_help} - show this help screen
    {key_exit} - exit the client
    {key_add_feed} - add a feed
    {key_delete} - delete the selected feed
    {key_reload} - reload/refresh feeds
    {key_save} - save episode for offline playback
    {key_up} - navigate up in menus
    {key_right} - navigate right in menus
    {key_down} - navigate down in menus
    {key_left} - navigate left in menus
    {key_scroll_up} - scroll up in menus
    {key_scroll_down} - scroll down in menus
    {key_play_selected} - play selected feed/episode
    {key_add_selected} - add selected feed/episode to queue
    {key_clear} - clear the queue
    {key_next} - go to the next episode in the queue
    {key_invert} - invert the order of the menu
    {key_mark_played} - mark episode as played/unplayed
    {key_pause_play|key_pause_play_alt} - pause/play the current episode
    {key_seek_forward|key_seek_forward_alt} - seek forward
    {key_seek_backward|key_seek_backward_alt} - seek backward
    {1-3} - change between client layouts
""" % (
    __title__,
    __version__,
    __date__,
    __author__,
    __author_email__,
    __license__,
    __url__
)
