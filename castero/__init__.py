__title__       = "castero"
__description__ = "Command line podcast client"
__author__      = "Jake Robertson <jake@faltro.com>"
__version__     = "0.1.0"
__date__        = "2018-03-31"
__copyright__   = "Copyright (c) 2018 Jake Robertson"
__license__     = "MIT License"
__url__         = "https://github.com/xgi/castero"

__help__ = """\
%s Help
============

Version: %s
Updated: %s
Maintainer: %s
License: %s
URL: %s

Commands
    h            - show this help screen
    q            - exit the client
    a            - add a feed
    d            - delete the selected feed
    r            - reload/refresh feeds
    arrows       - navigate menus
    page up/down - scroll menus
    enter        - play selected feed/episode
    space        - add selected feed/episode to queue
    c            - clear the queue
    p            - pause/play the current episode
    n            - go to the next episode in the queue
    f            - seek forward
    b            - seek backward
    

Press any key to exit this screen.
""" % (
    __title__,
    __version__,
    __date__,
    __author__,
    __license__,
    __url__
)
