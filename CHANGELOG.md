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

## 0.3.1 - 2018-09-15
**Fixed**
* Fixed an issue where config files would not properly migrate when a new
config section was added.

## 0.3.0 - 2018-09-15
**Added**
* Added a new "perspective" - a separate page for viewing your current queue.
You can switch through perspectives by using number keys -- 1 is the primary
perspective, 2 is the queue perspective.
* Added support for a custom download directory.
* Added support for text entry beyond the window width.

**Changed**
* The menu no longer automatically scrolls when playing an episode/feed (but it
still does when you only add the episode/feed to the queue).

**Fixed**
* Fixed a crash when opening the help menu with a short terminal.

## 0.2.6 - 2018-08-15
**Added**
* Added support for custom keybindings in the config.

**Fixed**
* Fixed an issue where the client would crash if a feed's description or title
field was missing.

## 0.2.5 - 2018-06-15
**Added**
* Added j/k/l as aliases for seek backward, pause/play, and seek forward,
respectively.
* Added support for inverting the list of feeds or episodes by pressing 'i' in
the corresponding menu. The order of episode lists is preserved, but the order
of the feeds list is not.

**Changed**
* Feeds are now ordered alphabetically.

## 0.2.4 - 2018-05-10
**Added**
* Added support for saving an entire feed at once.
* Handle -v or --version flag to display version instead of starting the
client.

**Changed**
* Deleting a feed will now delete all of its downloaded/saved episodes.

## 0.2.3 - 2018-05-03
**Added**
* Downloads will now be handled sequentially rather than in parallel.

**Changed**
* The client now explicitly requires VLC >= 2.2.3
* Revised text description for episodes/feeds with missing copyright tags.

**Fixed**
* Fixed an issue where pressing pause before the media had loaded would not
properly pause it.

## 0.2.2 - 2018-04-24
**Added**
* You can now delete a downloaded episode by pressing the save key again.
* Added a config option for asking for confirmation before deleting a feed.
* An error will now be raised on startup if dependencies are not met (VLC).
* Number of episodes are now shown in feed metadata.

**Changed**
* The client will no longer try to load media when a player is created. This
substantially improves performance when adding many episodes to a queue.

**Fixed**
* Fixed an issue where config files would not be properly migrated.

## 0.2.1 - 2018-04-22
**Added**
* Automatically migrate users' config file when the client updates and adds or
removes a new config option.
* The client will now properly resize when the size of the terminal changes.

**Changed**
* Metadata window will now properly extend to the right edge of the terminal.

**Fixed**
* Fixed an issue where the queue would not properly recognize that the current
episode had finished.
* Fixed footer text not being truncated, which caused errors if the screen size
was too small.

## 0.2.0 - 2018-04-20
**Added**
* Added support for downloading episodes for offline playback.

**Fixed**
* Fixed the description of some fields in the default config file.
* Fixed an issue where the client would not properly obey the reload_on_start 
config option.
* Fixed an issue where pressing enter or space with no feeds would crash the
client.

## 0.1.3 - 2018-04-19
**Added**
* Added config options for client colors.
* Added config option to automatically reload feeds on startup.
* Handle -h or --help flag to display help text instead of starting the client.

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