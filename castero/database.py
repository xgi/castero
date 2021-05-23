import json
import os
import sys
import sqlite3
import grequests
from typing import List
from io import StringIO

from castero import helpers
from castero.config import Config
from castero.datafile import DataFile
from castero.episode import Episode
from castero.feed import Feed, FeedError
from castero.queue import Queue
from castero.net import Net


class Database():
    """The user's database.

    This class provides an API for storing and retrieving data from an sqlite
    database file.

    The database replaces the Feeds class which stored feed/episode data in a
    JSON file. We automatically migrate users from that format to the database:
    see _create_from_old_feeds().

    For schema details, see $PACKAGE/templates/migrations.
    """
    PATH = os.path.join(DataFile.DATA_DIR, 'castero.db')
    OLD_PATH = os.path.join(DataFile.DATA_DIR, 'feeds')
    MIGRATIONS_DIR = os.path.join(DataFile.PACKAGE, 'templates/migrations')

    SQL_EPISODES_BY_FEED_WITH_PROGRESS = "select episode.id, episode.title, episode.description, episode.link, episode.pubdate, episode.copyright, episode.enclosure, episode.played, progress.time from episode left join progress on episode.id=progress.ep_id where feed_key=? order by episode.id"
    SQL_EPISODES_WITH_PROGRESS = "select episode.feed_key, episode.id, episode.title, episode.description, episode.link, episode.pubdate, episode.copyright, episode.enclosure, episode.played, progress.time from episode left join progress on episode.id=progress.ep_id order by episode.id"
    SQL_EPISODES_BY_ID = "select episode.feed_key, episode.id, episode.title, episode.description, episode.link, episode.pubdate, episode.copyright, episode.enclosure, episode.played, progress.time from episode left join progress on episode.id=progress.ep_id where episode.id=?"
    SQL_UNPLAYED_EPISODES_BY_FEED = "select episode.id, episode.title, episode.description, episode.link, episode.pubdate, episode.copyright, episode.enclosure, episode.played, progress.time from episode left join progress on episode.id=progress.ep_id where feed_key=? and played=0 order by episode.id"
    SQL_EPISODE_REPLACE = "replace into episode (id, title, feed_key, description, link, pubdate, copyright, enclosure, played)\nvalues (?,?,?,?,?,?,?,?,?)"
    SQL_EPISODE_REPLACE_NOID = "replace into episode (title, feed_key, description, link, pubdate, copyright, enclosure, played)\nvalues (?,?,?,?,?,?,?,?)"
    SQL_FEEDS_ALL = "select key, title, description, link, last_build_date, copyright from feed order by lower(title)"
    SQL_FEED_BY_KEY = "select key, title, description, link, last_build_date, copyright from feed where key=?"
    SQL_FEED_REPLACE = "replace into feed (key, title, description, link, last_build_date, copyright)\nvalues (?,?,?,?,?,?)"
    SQL_FEED_DELETE = "delete from feed where key=?"
    SQL_QUEUE_ALL = "select id, ep_id from queue"
    SQL_QUEUE_REPLACE = "replace into queue (id, ep_id)\nvalues (?,?)"
    SQL_QUEUE_DELETE = "delete from queue"
    SQL_EPISODE_PROGRESS_REPLACE = "replace into progress (ep_id, time)\nvalues (?,?)"
    SQL_EPISODE_PROGRESS_DELETE = "delete from progress where ep_id=?"

    def __init__(self):
        """
        If the database file does not exist but the old Feeds file does, we
        create the database using the old format.
        """
        existed = os.path.exists(self.PATH)
        DataFile.ensure_path(self.PATH)

        self._using_memory = not helpers.is_true(
            Config["restrict_memory_usage"])

        file_conn = sqlite3.connect(self.PATH, check_same_thread=False)

        if self._using_memory:
            memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._copy_database(file_conn, memory_conn)
            self._conn = memory_conn
        else:
            self._conn = file_conn

        if not existed and os.path.exists(self.OLD_PATH):
            self._create_from_old_feeds()

        self._conn.execute("PRAGMA foreign_keys = ON")
        self.migrate()

    def close(self):
        """Close the database.

        If we were using an in-memory copy of the data, it is written
        to the database file here.
        """
        if self._using_memory:
            DataFile.ensure_path(self.PATH)
            os.rename(self.PATH, self.PATH + ".old")

            file_conn = sqlite3.connect(self.PATH)
            self._copy_database(self._conn, file_conn)
        self._conn.close()

    def migrate(self):
        """Apply SQL migrations.

        Migrations are defined in $PACKAGE/templtaes/migrations.
        """
        cursor = self._conn.cursor()
        cur_version = cursor.execute('pragma user_version').fetchone()[0]

        migration_files = list(os.listdir(self.MIGRATIONS_DIR))
        for migration in sorted(migration_files):
            version = int(migration.split("-")[0])
            if version > cur_version:
                path = os.path.join(self.MIGRATIONS_DIR, migration)
                with open(path, 'rt') as f:
                    cursor.executescript(f.read())

    def _copy_database(self, from_connection, to_connection):
        """Copy database contents from one connection to another.
        """
        if sys.version_info.major == 3 and sys.version_info.minor >= 7:
            from_connection.backup(to_connection)
            return

        cursor = from_connection.cursor()
        cur_version = cursor.execute('pragma user_version').fetchone()[0]
        tempfile = StringIO()
        for line in from_connection.iterdump():
            tempfile.write('%s\n' % line)
        from_connection.close()
        tempfile.seek(0)

        to_connection.execute("PRAGMA user_version = " + str(cur_version))
        to_connection.cursor().executescript(tempfile.read())
        to_connection.commit()
        to_connection.execute("PRAGMA foreign_keys = ON")

    def _create_from_old_feeds(self):
        """Create database from deprecated Feeds format.

        This method is only necessary for users updating to version 0.4.0+ from
        an earlier version.
        """
        self.migrate()
        cursor = self._conn.cursor()

        with open(self.OLD_PATH, 'r') as f:
            content = json.loads(f.read())

        for key in content:
            feed_dict = content[key]

            cursor.execute(self.SQL_FEED_REPLACE, (
                key,
                feed_dict["title"],
                feed_dict["description"],
                feed_dict["link"],
                feed_dict["last_build_date"],
                feed_dict["copyright"]
            ))

            for episode_dict in feed_dict["episodes"]:
                cursor.execute(self.SQL_EPISODE_REPLACE_NOID, (
                    episode_dict["title"],
                    key,
                    episode_dict["description"],
                    episode_dict["link"],
                    episode_dict["pubdate"],
                    episode_dict["copyright"],
                    episode_dict["enclosure"],
                    False
                ))

        self._conn.commit()

    def delete_feed(self, feed: Feed) -> None:
        """Delete a feed from the database.

        Note: episodes have a cascade delete relation with their feed.

        Args:
            feed: the Feed to delete, which is in the database
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_FEED_DELETE, (feed.key,))
        self._conn.commit()

    def replace_feed(self, feed: Feed) -> None:
        """Replace (or insert) a feed in the database.

        This method is used for both updating a feed and for adding a new one.

        Args:
            feed: the Feed to replace
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_FEED_REPLACE, (
            feed.key,
            feed.title,
            feed.description,
            feed.link,
            feed.last_build_date,
            feed.copyright
        ))
        self._conn.commit()

    def replace_episode(self, feed: Feed, episode: Episode) -> None:
        """Replace (or insert) an episode in the database.

        This method is used for both updating an episode and for adding a new
        one.

        Episode instances have an ep_id field which is the episode's unique id
        in the database, if set. If it was not set when this method is called,
        we update it after the episode has been added to the database.

        Args:
            feed: the Feed the episode is a part of
            episode: the Episode to replace
        """
        cursor = self._conn.cursor()
        if episode.ep_id is None:
            cursor.execute(self.SQL_EPISODE_REPLACE_NOID, (
                episode.title,
                feed.key,
                episode.description,
                episode.link,
                episode.pubdate,
                episode.copyright,
                episode.enclosure,
                episode.played
            ))
            episode.ep_id = cursor.lastrowid
        else:
            cursor.execute(self.SQL_EPISODE_REPLACE, (
                episode.ep_id,
                episode.title,
                feed.key,
                episode.description,
                episode.link,
                episode.pubdate,
                episode.copyright,
                episode.enclosure,
                episode.played
            ))
        self._conn.commit()

    def replace_episodes(self, feed: Feed, episodes: List[Episode]) -> None:
        """Replace (or insert) a list of episodes in the database.

        This method is used for both updating episodes and for adding new ones.

        Args:
            feed: the Feed all episode are a part of
            episodes: a list of Episode's to replace
        """
        cursor = self._conn.cursor()

        # there are different sql queries depending on whether the episode
        # has an id, so we separate them into 2 operations
        episodes_without_id = []
        episodes_with_id = []

        for episode in episodes:
            if episode.ep_id is None:
                episodes_without_id.append(episode)
            else:
                episodes_with_id.append(episode)

        if len(episodes_without_id) > 0:
            cursor.executemany(self.SQL_EPISODE_REPLACE_NOID,
                               ((
                                   episode.title,
                                   feed.key,
                                   episode.description,
                                   episode.link,
                                   episode.pubdate,
                                   episode.copyright,
                                   episode.enclosure,
                                   episode.played
                               ) for episode in episodes_without_id)
                               )
        if len(episodes_with_id) > 0:
            cursor.executemany(self.SQL_EPISODE_REPLACE,
                               ((
                                   episode.ep_id,
                                   episode.title,
                                   feed.key,
                                   episode.description,
                                   episode.link,
                                   episode.pubdate,
                                   episode.copyright,
                                   episode.enclosure,
                                   episode.played
                               ) for episode in episodes_with_id)
                               )
        self._conn.commit()

    def delete_queue(self) -> None:
        """Clear the queue table.
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_QUEUE_DELETE)
        self._conn.commit()

    def replace_queue(self, queue: Queue) -> None:
        """Replace the queue in the database.

        This method overwrites the existing queue.

        Args:
            queue: the Queue to replace from
        """
        cursor = self._conn.cursor()

        self.delete_queue()

        i = 1
        for player in queue:
            episode = player.episode
            if self.episode(episode.ep_id) is not None:
                cursor.execute(self.SQL_QUEUE_REPLACE, (
                    i,
                    player.episode.ep_id
                ))
                i += 1
        self._conn.commit()

    def feeds(self) -> List[Feed]:
        """Retrieve the list of Feeds.

        Returns:
            List[Feed]: all Feed's in the database
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_FEEDS_ALL)

        feeds = []
        for row in cursor.fetchall():
            feed = Feed(
                url=row[0] if row[0].startswith('http') else None,
                file=row[0] if not row[0].startswith('http') else None,
                title=row[1],
                description=row[2],
                link=row[3],
                last_build_date=row[4],
                copyright=row[5]
            )

            if feed.title:
                feeds.append(feed)
            else:
                self.delete_feed(feed)
        return feeds

    def episodes(self, feed: Feed = None) -> List[Episode]:
        """Retrieve all episodes for a feed.

        Args:
            feed: the Feed to retrieve episodes of

        Returns:
            List[Episode]: all Episode's of the given Feed in the database
        """
        cursor = self._conn.cursor()

        if feed is None:
            cursor.execute(self.SQL_EPISODES_WITH_PROGRESS, ())
            rows = cursor.fetchall()

            feed_entries = {}
            for row in rows:
                feed_key = row[0]
                if feed_key not in feed_entries:
                    feed_entries[feed_key] = self.feed(feed_key)

            return [Episode(
                feed_entries[row[0]],
                ep_id=row[1],
                title=row[2],
                description=row[3],
                link=row[4],
                pubdate=row[5],
                copyright=row[6],
                enclosure=row[7],
                played=row[8],
                progress=row[9]
            )
                for row in rows]
        else:
            cursor.execute(
                self.SQL_EPISODES_BY_FEED_WITH_PROGRESS, (feed.key,))
            rows = cursor.fetchall()
            return self._create_feed_episode_list(feed, rows)

    def unplayed_episodes(self, feed: Feed) -> List[Episode]:
        """Retrieve all unplayed episodes for a feed.

        Args:
            feed: the Feed to retrieve episodes of

        Returns:
            List[Episode]: all Episode's of the given Feed in the database
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_UNPLAYED_EPISODES_BY_FEED, (feed.key,))
        rows = cursor.fetchall()
        return self._create_feed_episode_list(feed, rows)

    def _create_feed_episode_list(self, feed: Feed, episode_rows) -> List[Episode]:
        """Create a list of episode from feed episode query rows
        Args:
            feed: The feed the episodes are from,
            episode_rows: Query result rows
        Returns:
            List[Episode]: List of the episodes
        """
        return [Episode(
                feed,
                ep_id=row[0],
                title=row[1],
                description=row[2],
                link=row[3],
                pubdate=row[4],
                copyright=row[5],
                enclosure=row[6],
                played=row[7],
                progress=row[8]
                )
                for row in episode_rows]

    def feed(self, key) -> Feed:
        """Retrieve a feed by key.

        Args:
            key: the key of the Feed to retrieve, which is the feed's primary
            key in the database

        Returns:
            Feed: the matching Feed, if it exists, or None
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_FEED_BY_KEY, (key,))

        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return Feed(
                url=result[0] if result[0].startswith('http') else None,
                file=result[0] if not result[0].startswith('http') else None,
                title=result[1],
                description=result[2],
                link=result[3],
                last_build_date=result[4],
                copyright=result[5],
                episodes=[],
            )

    def episode(self, ep_id: int) -> Episode:
        """Retrieve an episode by ep_id.

        Args:
            ep_id: the id of the Episode to retrieve, which is the episode's
            primary key in the database

        Returns:
            Episode: the matching Episode, if it exists, or None
        """
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_EPISODES_BY_ID, (ep_id,))

        result = cursor.fetchone()
        if result is None:
            return None
        else:
            feed = self.feed(result[0])
            return Episode(
                feed,
                ep_id=result[1],
                title=result[2],
                description=result[3],
                link=result[4],
                pubdate=result[5],
                copyright=result[6],
                enclosure=result[7],
                played=result[8],
                progress=result[9],
            )

    def queue(self) -> List[Episode]:
        """Retrieve all episodes in the queue.

        Returns:
            List[Episode]: all Episode's in the queue
        """
        cursor = self._conn.cursor()

        # get ep_id's of episodes to retrieve
        cursor.execute(self.SQL_QUEUE_ALL, ())
        ep_ids = [row[1] for row in cursor.fetchall()]

        if len(ep_ids) == 0:
            return []

        # bulk retrieve all episodes
        sql = self.SQL_EPISODES_BY_ID
        for ep_id in ep_ids[1:]:
            sql += " OR id=?"
        cursor.execute(sql, tuple(ep_ids))

        episodes_cache = {}
        feeds_cache = {}
        for result in cursor.fetchall():
            ep_id = result[1]
            if ep_id not in episodes_cache:
                feed_key = result[0]
                feed = feeds_cache[feed_key] if feed_key in feeds_cache \
                    else self.feed(feed_key)
                episodes_cache[ep_id] = Episode(
                    feed,
                    ep_id=ep_id,
                    title=result[2],
                    description=result[3],
                    link=result[4],
                    pubdate=result[5],
                    copyright=result[6],
                    enclosure=result[7],
                    played=result[8],
                    progress=result[9]
                )

        # queue may contain repeated ep_id's, so we need to go back to the
        # retrieved ep_ids to get complete list of desired episodes
        return [episodes_cache[ep_id] for ep_id in ep_ids]

    def reload(self, display=None, feeds=None) -> None:
        """Reload feeds in the database.

        To preserve user metadata for episodes (such as played/marked status),
        we use Episode.replace_from() which "manually" copies such fields to
        the new downloaded episode. This is necessary because downloaded
        episodes are new Episode instances and we can't guarantee they have any
        of the same properties.

        Therefore, Episode.replace_from() _must_ be updated if any new user
        metadata fields are added.

        Also: to determine which episodes are the same in order to copy user
        metadata, we simply check whether the string representation of the two
        episodes are matching (usually the episodes' titles). This could cause
        issues if a feed has multiple episodes with the same title, although it
        does not require episode titles to be globally unique (that is,
        episodes with the same name in different feeds will never have issues).

        This method adheres to the max_episodes config parameter to limit the
        number of episodes saved per feed.

        Args:
            display: (optional) the display to write status updates to
            feeds: (optional) a list of feeds to reload. If not specified,
                all feeds in the database will be reloaded
        """
        if feeds is None:
            feeds = self.feeds()
        total_feeds = len(feeds)
        completed_feeds = 0
        errors = 0

        reqs = []
        url_pairs = {}
        file_feeds = []
        # Create async requests for each URL feed. We also keep a map from
        # each feed's URL to the Feed object itself in order to access the
        # object when a request completes (since the response object is all
        # that we are given).
        # We also keep track of file-based feeds, which are handled afterwards.
        for feed in feeds:
            if feed.key.startswith("http"):
                url_pairs[feed.key] = feed
                reqs.append(Net.GGet(feed.key))
            else:
                file_feeds.append(feed)

        # handle each response as downloads complete asynchronously
        for response in grequests.imap(reqs, size=3):
            if display is not None:
                error_str = "(%s errors)" % errors if errors > 0 else ""
                display.change_status(
                    "Reloading feeds (%d/%d) %s" % (completed_feeds, total_feeds, error_str))

            old_feed = None
            response_url = response.request.url
            if response_url in url_pairs:
                old_feed = url_pairs[response.request.url]
            elif hasattr(response, 'history') and len(response.history) > 0:
                response_url = response.history[0].url
                old_feed = url_pairs[response_url]
            else:
                errors += 1
                continue

            try:
                new_feed = Feed(url=response_url, response=response)
                self._reload_feed_data(old_feed, new_feed)
                completed_feeds += 1
            except FeedError:
                errors += 1

        # handle each file-based feed
        for old_feed in file_feeds:
            if display is not None:
                error_str = "(%s errors)" % errors if errors > 0 else ""
                display.change_status(
                    "Reloading feeds (%d/%d) %s" % (completed_feeds, total_feeds, error_str))

            try:
                new_feed = Feed(file=old_feed.key)
                self._reload_feed_data(old_feed, new_feed)
                completed_feeds += 1
            except FeedError:
                errors += 1

        if display is not None:
            display.change_status(
                "Successfully reloaded %d feeds" % total_feeds)
            display.menus_valid = False

    def replace_progress(self, episode: Episode, progress: int):
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_EPISODE_PROGRESS_REPLACE,
                       (episode.ep_id, progress))
        episode.progress = progress
        self._conn.commit()

    def delete_progress(self, episode: Episode):
        cursor = self._conn.cursor()
        cursor.execute(self.SQL_EPISODE_PROGRESS_DELETE, (episode.ep_id,))
        episode.progress = None
        self._conn.commit()

    def _reload_feed_data(self, old_feed: Feed, new_feed: Feed):
        """Helper method to update a feed and its episodes in the database.

        Args:
            old_feed: the original Feed to be replaced
            new_feed: a Feed with new/updated data
        """
        # keep user metadata for episodes intact
        new_episodes = new_feed.parse_episodes()
        old_episodes = self.episodes(new_feed)
        episode_progresses = {}
        for new_ep in new_episodes:
            matching_olds = [
                old_ep for old_ep in old_episodes if
                str(old_ep) == str(new_ep)
            ]
            if len(matching_olds) == 1:
                new_ep.replace_from(matching_olds[0])
                if (matching_olds[0].progress != 0):
                    episode_progresses[str(new_ep)] = new_ep.progress

        # limit number of episodes, if necessary
        max_episodes = int(Config["max_episodes"])
        if max_episodes != -1:
            new_episodes = new_episodes[:max_episodes]

        # update the feed and its episodes in the database
        self.replace_feed(new_feed)
        self.replace_episodes(new_feed, new_episodes)

        # ensure episodes have their progress carried over, if necessary
        added_episodes = self.episodes(new_feed)
        for episode in added_episodes:
            if str(episode) in episode_progresses:
                self.replace_progress(episode, episode.progress)
