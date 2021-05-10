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

## 0.9.2 - 2021-05-09
**Fixed**
* Fixed reloading feeds not propagating saved playback position.

## 0.9.1 - 2021-03-23
**Added**
* @tistatos - Playback position is saved/restored when restarting the
client.
* @tistatos - Created add_only_unplayed_episodes config option for
playing/queueing a feed.
* @DGambrinus - Maintain playback speed when playing different episodes.

**Changed**
* To improve performance, the client now (by default) uses an in-memory
database, which is only saved to disk when the client is closed. This
can be disabled with the restrict_memory_usage config option.
* Improved the performance of importing subscriptions (especially those
with many feeds).

**Fixed**
* @tistatos - Fixed episode data not being deleted when removing feeds.
* Fixed player volume occasionally not being retained when switching
between episodes.
* Fixed exception with terminals that don't support an invisible cursor
mode.
* Fixed reload operation failing when reloading one feed would fail in a
specific way.

## 0.8.2 - 2020-08-23
**Added**
* Added a config option for the default playback volume.

**Fixed**
* Fixed new episodes not being properly sorted in the menu.
* Fixed detection for feeds with an empty title tag (they still aren't
allowed, but we explicitly check for this now).

## 0.8.1 - 2020-07-26
**Added**
* Added the `e` key to execute a system command on an episode. Command can
be configured with the `execute_command` option.
* Added volume control keybinds.
* Added config options to use a proxy.

**Changed**
* Made the help menu scrollable.
* Made separate keybinds for saving/deleting episodes for offline
playback (`s` and `x` by default). Existing configs will be migrated.

**Fixed**
* Fixed an issue where feeds would, on some systems, not be displayed in order.
* Fixed poor UI performance when reloading feeds.
* Fixed time/duration display not being properly justified - Thanks @buck10!
* Fixed an issue importing a certain structure of OPML subscriptions.
* Fixed an issue with episode IDs being reset when feeds are reloaded.

## 0.8.0 - 2020-02-22
**Added**
* Made database operations multi-threaded to improve performance, especially
for users with many feeds.
* Added the `u` key for displaying an episode URL in the status bar - Thanks
@jose1711!
* Added a perspective to display downloaded episodes. Press `4` to access it.

**Changed**
* Reduced the default input timeout, which is tied to the display refresh rate.
This will somewhat increase standby CPU usage. Users with low-end systems may
wish to increase this timeout with the `refresh_delay` config setting.
* Improved reporting of errors when importing OPML files - Thanks @hebecked!
* Improved the overall UX of importing OPML files, with "live" database changes
and status reports.
* Changed the file naming format for downloaded episodes. Episodes downloaded
in earlier versions of castero will not be detected and must be re-downloaded.

**Fixed**
* Fixed stderr file descriptor not being found on macOS, causing a crash.
* Fixed the reloading status message to properly show the current feed number.

## 0.7.0 - 2019-12-13
**Added**
* Added support for filtering menus with the `/` key.
* Added individual config options for foreground text colors.
* Added an option for default playback speed.
* Added the number of unplayed episodes to the menu header.

**Fixed**
* Fixed support for OPML v2.
* Fixed menu headers using the wrong background color.
* Fixed the metadata window not properly filling the screen height.
* Fixed the selected menu index being offscreen when resizing the window.
* Fixed menu selections not being sanitized in the correct sequence.
* Fixed menus not visually updating when modified.
* Fixed ffmpeg output appearing in the client - Thanks @rien333 and @jaseg!
* Fixed a crash when resizing the window at some ratios.
* Fixed a crash when trying to invert menus.
* Fixed a crash when an episode had no audio enclosure.
* Fixed a crash when episode enclosure caused a request exception.
* Fixed a crash when trying to play the current episode in the queue.

## 0.6.0 - 2019-06-10
**Added**
* Added support for importing/exporting subscriptions to and from OPML files.
Many other clients support this format, so you are now able to easily move your
feeds between clients. To use this feature, run castero with the
`--import` or `--export` flag (or run `castero -h` for more info).
* Added support for preserving the queue when restarting the client.
* Added support for 256 colors - Thanks @arza-zara!
* Added controls for playback speed - **[** and **]** by default.

**Fixed**
* Fixed a crash when viewing metadata for a feed with no description.
* Fixed custom_download_dir config option not being an absolute path.
* Improved scroll performance of episode menu with many episodes.
* Fixed a crash when vertically shrinking the client.

## 0.5.5 - 2019-05-18
**Added**
* Added the name of the feed to episodes in the queue menu/perspective.

**Fixed**
* Fixed client not adhering to the max_episodes config option when reloading.
* Fixed the queue not progressing automatically on episode completion.
* Fixed a Python 3.5 compatibility issue.

## 0.5.4 - 2019-04-13
**Added**
* Added download status "\[D\]" metadata tag to episode menu.

**Fixed**
* Fixed a crash when queueing a large number of episodes with the VLC player.
* Fixed delay when skipping ahead in queue.
* Fixed a crash when running with Python 3.5.
* Fixed crash when trying to create database file in nonexistant directory.
* Fixed episode menu not updating on feed delete.
* Fixed menus not updating when terminal dimensions change.
* Fixed user metadata (i.e. played status) being overwritten when reloading.

## 0.5.3 - 2019-03-19
**Fixed**
* Fixed some files not being properly linked on install.

## 0.5.0 - 2019-03-19
**Added**
* The client now uses an sqlite database file for storing data (sqlite added as
a dependency).
* Added support for marking episodes as played.
* Added a metadata-less perspective (SimplePerspective) accessed with `3`.

**Changed**
* Menus are now able to update dynamically from the database.

**Deprecated**
* The old JSON `feeds` file is no longer used, in favor of a `castero.db` file
in the same location. The client will migrate your `feeds` file to the new
database upon starting if necessary. There are no known issues with this
process, but your original file is not modified regardless (please create an
Issue if you have any problems!).

**Fixed**
* Fixed a crash when trying to view the metadata of 0 episodes.

## 0.4.2 - 2019-03-02
**Added**
* Added a separate config option for seeking forwards/backwards - Thanks
@mtostenson!

**Changed**
* FeedErrors will give more descriptive information in the status bar.

**Fixed**
* Fixed a potential crash when trying to run without libmpv.
* Fixed a crash when an unused player library is uninstalled.
* Fixed an issue where some websites would block the client since it did not
send requests with a user agent.

## 0.4.1 - 2019-02-12
**Added**
* Added support for extracting plaintext from HTML metadata descriptions (can
be disabled in config).
* Added an option for right-aligning episode time/duration.
* Added an option to limit the number of episodes in a feed.
* Added an option to disable the default status message.
* Added perspective keys to help menu.

**Fixed**
* mpv support now uses the python-mpv library instead of pympv, which may fix
installation problems for some users.
* Fixed an issue where client could crash when adding episodes to queue while
using mpv.
* Fixed a crash when trying to determine whether mpv/libmpv was available.
* Fixed a crash when trying to delete nothing on queuelisting perspective.
* Fixed a crash when going to episodes menu for a feed with no episodes.
* Fixed incomplete metadata being displayed when viewing a feed with a single
episode.

## 0.4.0 - 2019-01-26
**Added**
* Added support for playback with mpv as an alternative to VLC.
* Added foundational support for displaying metadata in menus (i.e. download
status) - Thanks @nbastin!
* Added support for background transparency (if available on your terminal
emulator) - Thanks @aneum7!
* Added an option for disabling vertical bars/borders between menus.

**Fixed**
* Fixed an issue where the client would attempt to download remote media while
offline - Thanks @nbastin!
* Fixed an issue where the client would sometimes break your config while
trying to migrate items with blank values.
* Prevented crashing on some download errors; instead, a status/error message
is displayed - Thanks @nbastin!
* Improved wrapping support for CJK text - Thanks @Rand01ph!
* Updated Requests version in response to CVE-2018-18074.


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