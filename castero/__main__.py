from castero.display import Display
from castero.config import Config
from castero.feeds import Feeds
import castero
import sys
import curses


def main():
    # check if user is running the client with -h or --help flag
    help_flags = ['-h', '--help']
    if sys.argv[len(sys.argv) - 1] in help_flags:
        print(castero.__help__)
        sys.exit(0)

    config = Config()
    feeds = Feeds()

    stdscr = curses.initscr()
    display = Display(stdscr, config, feeds)

    display.clear()
    display.update_parent_dimensions()

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
