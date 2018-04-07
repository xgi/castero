from castero.display import Display
from castero.config import Config
from castero.feeds import Feeds
import sys


def main():
    config = Config()
    feeds = Feeds()

    display = Display(config=config, feeds=feeds)
    display.loop()
    sys.exit(0)


main()
