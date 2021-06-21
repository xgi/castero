__title__ = "castero"
__description__ = "A TUI podcast client for the terminal"
__keywords__ = "podcast commandline terminal tui curses"
__author__ = "Jake Robertson"
__author_email__ = "jake@faltro.com"
__version__ = "0.9.3"
__date__ = "2021-06-20"
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
    {key_remove} - remove the selected feed
    {key_reload} - reload all feeds
    {key_reload_selected} - reload the selected feed
    {key_save} - save episode for offline playback
    {key_delete} - delete downloaded episodes
    {key_up/key_down} - navigate up/down in menus
    {key_right/key_left} - navigate right/left in menus
    {key_scroll_up/key_scroll_down} - scroll up/down in menus
    {key_play_selected} - play selected feed/episode
    {key_add_selected} - add selected feed/episode to queue
    {key_clear} - clear the queue
    {key_clear_progress} - clear progress of selected episode
    {key_next} - go to the next episode in the queue
    {key_invert} - invert the order of the menu
    {key_filter} - filter the contents of the menu
    {key_mark_played} - mark episode as played/unplayed
    {key_pause_play|key_pause_play_alt} - pause/play the current episode
    {key_seek_forward|key_seek_forward_alt} - seek forward
    {key_seek_backward|key_seek_backward_alt} - seek backward
    {key_volume_increase/key_volume_decrease} - increase/decrease volume
    {key_rate_increase/key_rate_decrease} - increase/decrease playback speed
    {key_show_url} - show episode URL
    {1-5} - change between client layouts
""" % (
    __title__,
    __version__,
    __date__,
    __author__,
    __author_email__,
    __license__,
    __url__
)
