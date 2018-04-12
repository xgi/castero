from castero.display import Display
from castero.config import Config
from castero.feeds import Feeds
import sys
import curses


def main():
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
