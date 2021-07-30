# castero

[![GitHub release](https://img.shields.io/github/release/xgi/castero.svg?style=flat-square)](https://github.com/xgi/castero/releases) [![PyPI](https://img.shields.io/pypi/v/castero.svg?style=flat-square)](https://pypi.org/project/castero) [![GitHub Build](https://img.shields.io/github/workflow/status/xgi/castero/CI?style=flat-square)](https://circleci.com/gh/xgi/castero/tree/master) [![Maintainability](https://api.codeclimate.com/v1/badges/babcaad5cb2cca266c92/maintainability)](https://codeclimate.com/github/xgi/castero/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/babcaad5cb2cca266c92/test_coverage)](https://codeclimate.com/github/xgi/castero/test_coverage)

castero is a TUI podcast client for the terminal.

![example client screenshot](https://raw.githubusercontent.com/xgi/castero/master/res/client_example.png)

## Installation

Install from [PyPi](https://pypi.org/project/castero) with pip:

```bash
$ pip3 install castero
```

Upgrading:

```bash
$ pip3 install castero --upgrade
```

### Manual Installation

```bash
$ git clone https://github.com/xgi/castero
$ cd castero
$ sudo python setup.py install
```

## Dependencies

Running castero requires the following external dependencies:

* Python >= 3.5 (check the output of ``python --version``)
* sqlite3
* At least one of the following media players:
  * vlc >= 2.2.3
  * (mpv and libmpv) >= 0.14.0
  
## Usage

After installing castero, it can be run with simply:

```bash
$ castero
```

The help menu provides a list of controls and can be accessed by pressing
<kbd>h</kbd>. Alternatively, see the list below:

```text
Commands
    h           - show this help screen
    q           - exit the client
    a           - add a feed
    d           - delete the selected feed
    r           - reload/refresh feeds
    s           - save episode for offline playback
    UP/DOWN     - navigate up/down in menus
    RIGHT/LEFT  - navigate right/left in menus
    PPAGE/NPAGE - scroll up/down in menus
    ENTER       - play selected feed/episode
    SPACE       - add selected feed/episode to queue
    c           - clear the queue
    n           - go to the next episode in the queue
    i           - invert the order of the menu
    /           - filter the contents of the menu
    m           - mark episode as played/unplayed
    p or k      - pause/play the current episode
    f or l      - seek forward
    b or j      - seek backward
    =/-         - increase/decrease volume
    ]/[         - increase/decrease playback speed
    u           - show episode URL
    1-5         - change between client layouts
```

### Importing/exporting feeds from another client

castero supports importing and exporting an [OPML file](https://en.wikipedia.org/wiki/OPML)
of your subscriptions in order to easily transfer them between other podcast
clients. Please refer to your other client's documentation for details on
how/if it supports this format.

Importing and exporting from castero are available with command line flags.
Run `castero --help` for details.

## Configuration

The configuration file is located at `{HOME}/.config/castero/castero.conf`
after the client has been run at least once.

Please see the [default castero.conf](https://github.com/xgi/castero/blob/master/castero/templates/castero.conf)
for a list of available settings.

User data, including downloaded episodes and a database with your feed
information, is located at `{HOME}/.local/share/castero/`. These files are not
intended to be manually modified. Removing the database will simply cause
castero to replace it with an empty one the next time you run the client.

## Testing

This project uses [pytest](https://pytest.org) for testing. To run tests, run
the following command in the project's root directory:

```bash
$ python -m pytest tests
```

You can also run tests for an individual unit, i.e.:

```bash
$ python -m pytest tests/test_feed.py
```

## License

[MIT License](https://github.com/xgi/castero/blob/master/LICENSE.txt)
