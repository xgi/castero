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
    # check if user is running the client with -h or --help flag
    help_flags = ['-h', '--help']
    if sys.argv[len(sys.argv) - 1] in help_flags:
        print(castero.__help__)
        sys.exit(0)

    # check whether dependencies are met
    Player.check_dependencies()

    config = Config()
    feeds = Feeds()

    stdscr = curses.initscr()
    display = Display(stdscr, config, feeds)

    display.clear()
    display.update_parent_dimensions()

    if helpers.is_true(config['reload_on_start']):
        t = threading.Thread(target=feeds.reload, args=[display])
        t.start()

    running = True
    while running:
        display.display()
        display.update()
        display.refresh()
        c = display.getch()
        if c != -1:
            running = display.handle_input(c)

    sys.exit(0)


main()
