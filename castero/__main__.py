import sys
import curses
import threading
import castero
from castero import helpers
from castero.display import Display
from castero.config import Config
from castero.feeds import Feeds
from castero.player import Player


def main():
    # check if user is running the client with an info flag
    info_flags = {
        'help': ['-h', '--help'],
        'version': ['-v', '--version']
    }
    if sys.argv[len(sys.argv) - 1] in info_flags['help']:
        print(castero.__help__)
        sys.exit(0)
    elif sys.argv[len(sys.argv) - 1] in info_flags['version']:
        print(castero.__version__)
        sys.exit(0)

    # check whether dependencies are met
    Player.check_dependencies()

    # instantiate DataFile-based objects
    config = Config()
    feeds = Feeds()

    # instantiate the display object
    stdscr = curses.initscr()
    display = Display(stdscr, config, feeds)
    display.clear()
    display.update_parent_dimensions()

    # check if we need to start reloading
    if helpers.is_true(config['reload_on_start']):
        reload_thread = threading.Thread(target=feeds.reload, args=[display])
        reload_thread.start()

    # core loop for the client
    running = True
    while running:
        display.display()
        display.update()
        display.refresh()
        char = display.getch()
        if char != -1:
            running = display.handle_input(char)

    sys.exit(0)


main()
