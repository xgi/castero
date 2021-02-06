import curses
import sys
import threading
import re
import argparse
import os
import io
import ctypes
import tempfile

from gevent import monkey
monkey.patch_all(thread=False, select=False)

import castero
from castero import helpers
from castero.config import Config
from castero.database import Database
from castero.display import Display
from castero.feed import Feed
from castero.subscriptions import Subscriptions


def import_subscriptions(path: str, database: Database) -> None:
    subscriptions = Subscriptions()

    # Load may raise an error, but they are user-friendly enough that we don't
    # need to catch them here. It's also okay to crash at this point.
    subscriptions.load(path)

    for generated in subscriptions.parse():
        if isinstance(generated, Feed):
            feed = generated
            database.replace_feed(feed)
            episodes = feed.parse_episodes()
            database.replace_episodes(feed, episodes)
            print("Added \"%s\" with %d episodes" % (str(feed), len(episodes)))
        else:
            print("ERROR: Failed to load %s -- %s" %
                  (str(generated[0]), str(generated[1])))

    database.close()
    print("Imported %d feeds" % len(subscriptions.feeds))


def export_subscriptions(path: str, database: Database) -> None:
    subscriptions = Subscriptions()

    feeds = database.feeds()
    subscriptions.generate(feeds)
    # Save may raise an error, but they are user-friendly enough that we don't
    # need to catch them here. It's also okay to crash at this point.
    subscriptions.save(path)

    print("Exported %d feeds" % len(feeds))


def redirect_stderr() -> io.TextIOWrapper:
    temp_file = tempfile.TemporaryFile(prefix="%s-" % castero.__title__)

    # get os-specific stderr descriptor
    stderr = 'stderr'
    if sys.platform == 'darwin':
        stderr = '__stderrp'

    libc = ctypes.CDLL(None)
    c_stderr = ctypes.c_void_p.in_dll(libc, stderr)

    stderr_fd = sys.stderr.fileno()
    libc.fflush(c_stderr)
    sys.stderr.close()

    # make the stderr fd point to the temp_file
    os.dup2(temp_file.fileno(), stderr_fd)

    # overwrite sys.stderr to use our modified fd
    # - not explicitly necessary for our purposes, since curses does not
    #   use this field
    sys.stderr = io.TextIOWrapper(os.fdopen(stderr_fd, 'wb'))

    return temp_file.fileno()


def main():
    database = Database()

    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog=castero.__title__, description=castero.__description__)
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s {}'.format(castero.__version__))
    parser.add_argument('--import', help='path to OPML file of feeds to add')
    parser.add_argument('--export', help='path to save feeds as OPML file')
    args = parser.parse_args()

    if vars(args)['import'] is not None:
        import_subscriptions(vars(args)['import'], database)
        sys.exit(0)
    elif vars(args)['export'] is not None:
        export_subscriptions(vars(args)['export'], database)
        sys.exit(0)

    # update fields in help menu text
    for field in Config:
        if "{%s}" % field in castero.__help__:
            castero.__help__ = \
                castero.__help__.replace(
                    "{%s}" % field,
                    Config[field].ljust(11)
                )
        elif "{%s|" % field in castero.__help__:
            field2 = castero.__help__.split("{%s|" % field)[1].split("}")[0]
            castero.__help__ = \
                castero.__help__.replace(
                    "{%s|%s}" % (field, field2),
                    ("%s or %s" % (Config[field], Config[field2])).ljust(11)
                )
        elif "{%s/" % field in castero.__help__:
            field2 = castero.__help__.split("{%s/" % field)[1].split("}")[0]
            castero.__help__ = \
                castero.__help__.replace(
                    "{%s/%s}" % (field, field2),
                    ("%s/%s" % (Config[field], Config[field2])).ljust(11)
                )
    remaining_brace_fields = re.compile('\\{.*?\\}').findall(castero.__help__)
    for field in remaining_brace_fields:
        adjusted = field.replace("{", "").replace("}", "").ljust(11)
        castero.__help__ = \
            castero.__help__.replace(field, adjusted)

    # instantiate display
    redirect_stderr()
    stdscr = curses.initscr()
    display = Display(stdscr, database)
    display.clear()
    display.update_parent_dimensions()

    # check if we need to start reloading
    if helpers.is_true(Config['reload_on_start']):
        reload_thread = threading.Thread(
            target=database.reload,
            args=[display]
        )
        reload_thread.start()

    # run initial display operations
    display.display_all()
    display._menus_valid = False
    display._update_timer = 0

    # core loop for the client
    running = True
    while running:
        display.display()
        char = display.getch()
        if char != -1:
            running = display.handle_input(char)

    sys.exit(0)


main()
