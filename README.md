# castero

[![GitHub release](https://img.shields.io/github/release/xgi/castero.svg)](https://github.com/xgi/castero/releases) [![Build Status](https://travis-ci.org/xgi/castero.svg?branch=master)](https://travis-ci.org/xgi/castero) [![codecov](https://codecov.io/gh/xgi/castero/branch/master/graph/badge.svg)](https://codecov.io/gh/xgi/castero)

castero is a podcast client for the command line.

![client_example](res/client_example.png)

## Installation

castero is not yet available on PyPi.

### Manual Installation

```bash
$ git clone https://github.com/xgi/castero
$ cd castero
$ sudo python setup.py install
```

## Dependencies

Running castero requires the following external dependencies:

* vlc

## Usage

After installing castero, it can be run with simply:
```bash
$ castero
```

The help menu provides a list of controls and can be accessed by pressing <kbd>h</kbd>. Alternatively, see the list below:
```
Commands
    h            - show this help screen
    q            - exit the client
    a            - add a feed
    d            - delete the selected feed
    arrows       - navigate menus
    page up/down - scroll menus
    enter        - play selected feed/episode
    space        - add selected feed/episode to queue
    c            - clear the queue
    p            - pause/play the current episode
    n            - go to the next episode in the queue
    f            - seek forward
    b            - seek backward
```

## Configuration

The configuration file is located at `{HOME}/.config/castero/` after the client has been run at least once.

Please see [castero.conf](castero/templates/castero.conf) for a list of available settings.

Additionally, a file containing your list of feeds is located at `{HOME}/.local/share/castero/feeds`. This file is provided to avoid redownloading feeds on every startup. However, it is not intended to be manually modified. Removing this file will simply cause castero to replace it with an empty list next time you run the client.

## Testing

This project uses [PyTest](https://pytest.org) for testing. To run tests, run the following command in the project's root directory:
```bash
python -m pytest tests
```
You can also run tests for an individual unit, i.e.:
```bash
python -m pytest tests/test_feed.py
```

## License

[MIT License](LICENSE.txt)