import curses
import sys
import threading
import re
import argparse

import castero
from castero import helpers
from castero.config import Config
from castero.database import Database
from castero.display import Display
from castero.player import Player
from castero.subscriptions import Subscriptions, SubscriptionsLoadError


def import_subscriptions(path: str, database: Database) -> None:
    subscriptions = Subscriptions()

    # Load may raise an error, but they are user-friendly enough that we don't
    # need to catch them here. It's also okay to crash at this point.
    subscriptions.load(path)

    print("Importing %d feeds..." % len(subscriptions.feeds))

    for feed in subscriptions.feeds:
        database.replace_feed(feed)
        episodes = feed.parse_episodes()
        database.replace_episodes(feed, episodes)
        print("Imported '%s' with %d episodes" % (str(feed), len(episodes)))


def export_subscriptions(path: str, database: Database) -> None:
    subscriptions = Subscriptions()
    
    feeds = database.feeds()
    subscriptions.generate(feeds)
    # Save may raise an error, but they are user-friendly enough that we don't
    # need to catch them here. It's also okay to crash at this point.
    subscriptions.save(path)

    print("Exported %d feeds" % len(feeds))


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

    # instantiate display
    stdscr = curses.initscr()
    display = Display(stdscr, database)
    display.clear()
    display.update_parent_dimensions()

    # check if we need to start reloading
    if helpers.is_true(Config['reload_on_start']):
        reload_thread = threading.Thread(target=database.reload, args=[display])
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
