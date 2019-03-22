import curses
import sys
import threading
import re

import castero
from castero import helpers
from castero.config import Config
from castero.database import Database
from castero.display import Display
from castero.player import Player


def main():
    database = Database()

    # update fields in help menu text
    for field in Config:
        if "{%s}" % field in castero.__help__:
            castero.__help__ = \
                castero.__help__.replace(
                    "{%s}" % field,
                    Config[field].ljust(9)
                )
        elif "{%s|" % field in castero.__help__:
            field2 = castero.__help__.split("{%s|" % field)[1].split("}")[0]
            castero.__help__ = \
                castero.__help__.replace(
                    "{%s|%s}" % (field, field2),
                    ("%s or %s" % (Config[field], Config[field2])).ljust(9)
                )
    remaining_brace_fields = re.compile('\{.*?\}').findall(castero.__help__)
    for field in remaining_brace_fields:
        adjusted = field.replace("{", "").replace("}", "").ljust(9)
        castero.__help__ = \
            castero.__help__.replace(field, adjusted)

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

    # instantiate the display object
    stdscr = curses.initscr()
    display = Display(stdscr, database)
    display.clear()
    display.update_parent_dimensions()

    # check if we need to start reloading
    if helpers.is_true(Config['reload_on_start']):
        reload_thread = threading.Thread(target=feeds.reload, args=[display])
        reload_thread.start()

    # run initial display operations
    display.display()
    display.update()
    display.refresh()

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
