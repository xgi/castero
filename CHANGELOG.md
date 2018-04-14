# castero changelog

This changelog generally follows the principles outlined at
<https://keepachangelog.com>, although the format may differ slightly.

Version listings include the following sections, if applicable:
* Added - for new features
* Changed - for changes to existing functionality
* Deprecated - for pre-existing features made obsolete or unsupported
* Removed - for removed features or functionality
* Fixed - for bugs fixed

See also <https://github.com/xgi/castero/releases>.

## 0.1.2 - 2018-04-13
**Added**
* You can now add entire feeds to the queue.
* Running the client with too small a screen (minimum arbitrarily defined at 20
cols and 8 lines) will now raise an error.

**Changed**
* Reloading feeds now runs on a separate thread to allow the user to continue
interacting with the client.
* Refactored setup.py with additional args in preparation for PyPi upload.

**Fixed**
* Fixed an issue where reloading feeds caused the user's selection to remain in
the episodes menu, resulting in strange behavior.
* Fixed an issue where status messages would overlap with each other after
being replaced.

## 0.1.1 - 2018-04-12
**Added**
* Pressing 'r' will now reload/refresh your feeds list.
* Added support for showing status messages in the footer, and certain commands
will now display status messages after running (or if an error occurs).

**Fixed**
* Fixed an issue where recreating menus often caused them to be smaller than
normal.
* Fixed an issue where a feeds file with duplicate keys would not load.