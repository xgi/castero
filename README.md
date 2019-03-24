# castero

[![GitHub release](https://img.shields.io/github/release/xgi/castero.svg)](https://github.com/xgi/castero/releases) [![PyPI](https://img.shields.io/pypi/v/castero.svg)](https://pypi.org/project/castero) [![CircleCI](https://circleci.com/gh/xgi/castero/tree/master.svg?style=svg)](https://circleci.com/gh/xgi/castero/tree/master) [![Codacy Grade](https://api.codacy.com/project/badge/Grade/f67d09d07b1d4d1aa1c97db3cbed5d1f)](https://www.codacy.com/app/xgi/castero) [![Codacy Coverage](https://api.codacy.com/project/badge/Coverage/f67d09d07b1d4d1aa1c97db3cbed5d1f)](https://www.codacy.com/app/xgi/castero)

castero is a TUI podcast client for the terminal.

![example client screenshot](https://raw.githubusercontent.com/xgi/castero/master/res/client_example.png)

## Installation

Install from [PyPi](https://pypi.org/project/castero) with pip:

```bash
$ pip install castero
```

Upgrading:

```bash
$ pip install castero --upgrade
```

### Manual Installation

Warning: changes to the master branch are sometimes made before the
documentation on this page is updated.

```bash
$ git clone https://github.com/xgi/castero
$ cd castero
$ sudo python setup.py install
```

## Dependencies

Running castero requires the following external dependencies:

* Python >= 3.5 (check the output of ``python --version``)
* sqlite3
* **One** of the following media players:
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
    h            - show this help screen
    q            - exit the client
    a            - add a feed
    d            - delete the selected feed
    r            - reload/refresh feeds
    s            - save episode for offline playback
    arrows       - navigate menus
    page up/down - scroll menus
    enter        - play selected feed/episode
    space        - add selected feed/episode to queue
    c            - clear the queue
    n            - go to the next episode in the queue
    i            - invert the order of the menu
    p or k       - pause/play the current episode
    f or l       - seek forward
    b or j       - seek backward
    1-3          - change between client layouts
```

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