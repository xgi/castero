import json
import os
import sqlite3
from typing import List, Tuple

from castero import helpers
from castero.config import Config
from castero.datafile import DataFile
from castero.episode import Episode
from castero.feed import Feed


class Database():
    """The Database class.

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

    def __init__(self):
        """Initializes the object.

        If the database file does not exist but the old Feeds file does, we
        create the database using the old format.
        """
        existed = os.path.exists(self.PATH)
        DataFile.ensure_path(self.PATH)
        self._conn = sqlite3.connect(self.PATH, check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")

        if not existed and os.path.exists(self.OLD_PATH):
            self._create_from_old_feeds()

        self.migrate()

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

            sql = "insert into feed (key, title, description, link, last_build_date, copyright)\n" \
                  "values (?,?,?,?,?,?)"
            cursor.execute(sql, (
                key,
                feed_dict["title"],
                feed_dict["description"],
                feed_dict["link"],
                feed_dict["last_build_date"],
                feed_dict["copyright"]
            ))

            for episode_dict in feed_dict["episodes"]:
                sql = "insert into episode (feed_key, title, description, link, pubdate, copyright, enclosure)\n" \
                      "values (?,?,?,?,?,?,?)"
                cursor.execute(sql, (
                    key,
                    episode_dict["title"],
                    episode_dict["description"],
                    episode_dict["link"],
                    episode_dict["pubdate"],
                    episode_dict["copyright"],
                    episode_dict["enclosure"]
                ))

        self._conn.commit()

    def delete_feed(self, feed: Feed) -> None:
        """Delete a feed from the database.

        Note: episodes have a cascade delete relation with their feed.

        Args:
            feed: the Feed to delete, which is in the database
        """
        sql = "delete from feed where key=?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (feed.key,))
        self._conn.commit()

    def replace_feed(self, feed: Feed) -> None:
        """Replace (or insert) a feed in the database.

        This method is used for both updating a feed and for adding a new one.

        Args:
            feed: the Feed to replace
        """
        sql = "replace into feed (key, title, description, link, last_build_date, copyright)\n" \
              "values (?,?,?,?,?,?)"
        cursor = self._conn.cursor()
        cursor.execute(sql, (
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
            sql = "replace into episode (title, feed_key, description, link, pubdate, copyright, enclosure, played)\n" \
                "values (?,?,?,?,?,?,?,?)"
            cursor.execute(sql, (
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
            sql = "replace into episode (id, title, feed_key, description, link, pubdate, copyright, enclosure, played)\n" \
                "values (?,?,?,?,?,?,?,?,?)"
            cursor.execute(sql, (
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
        for episode in episodes:
            self.replace_episode(feed, episode)
        self._conn.commit()

    def feeds(self) -> List[Feed]:
        """Retrieve the list of Feeds.

        Returns:
            List[Feed]: all Feed's in the database
        """
        sql = "select key, title, description, link, last_build_date, copyright from feed"
        cursor = self._conn.cursor()
        cursor.execute(sql)

        feeds = []
        for row in cursor.fetchall():
            feeds.append(Feed(
                url=row[0] if row[0].startswith('http') else None,
                file=row[0] if not row[0].startswith('http') else None,
                title=row[1],
                description=row[2],
                link=row[3],
                last_build_date=row[4],
                copyright=row[5]
            ))
        return feeds

    def episodes(self, feed: Feed) -> List[Episode]:
        """Retrieve all episodes for a feed.

        Args:
            feed: the Feed to retrieve episodes of

        Returns:
            List[Episode]: all Episode's of the given Feed in the database
        """
        sql = "select id, title, description, link, pubdate, copyright, enclosure, played from episode where feed_key=?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (feed.key,))

        episodes = []
        for row in cursor.fetchall():
            episodes.append(Episode(
                feed,
                ep_id=row[0],
                title=row[1],
                description=row[2],
                link=row[3],
                pubdate=row[4],
                copyright=row[5],
                enclosure=row[6],
                played=row[7]
            ))
        return episodes

    def feed(self, key) -> Feed:
        """Retrieve a feed by key.

        Args:
            key: the key of the Feed to retrieve, which is the feed's primary
            key in the database

        Returns:
            Feed: the matching Feed, if it exists, or None
        """
        sql = "select key, title, description, link, last_build_date, copyright from feed where key=?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (key,))

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
        sql = "select feed_key, id, title, description, link, pubdate, copyright, enclosure, played from episode where id=?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (ep_id,))

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
                played=result[8]
            )

    def reload(self, display=None) -> None:
        """Reload all feeds in the database.

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
        """
        feeds = self.feeds()
        total_feeds = len(feeds)
        current_feed = 1

        for feed in self.feeds():
            if display is not None:
                display.change_status(
                    "Reloading feeds (%d/%d)" % (current_feed, total_feeds)
                )

            # assume urls have http in them
            if "http" in feed.key:
                new_feed = Feed(url=feed.key)
            else:
                new_feed = Feed(file=feed.key)

            # keep user metadata for episodes intact
            new_episodes = new_feed.parse_episodes()
            old_episodes = self.episodes(feed)
            for new_ep in new_episodes:
                matching_olds = [
                    old_ep for old_ep in old_episodes if str(old_ep) == str(new_ep)]
                if len(matching_olds) == 1:
                    new_ep.replace_from(matching_olds[0])

            # limit number of episodes, if necessary
            max_episodes = int(Config["max_episodes"])
            if max_episodes != -1:
                new_episodes = new_episodes[:max_episodes]

            self.replace_feed(new_feed)
            self.replace_episodes(new_feed, new_episodes)

        if display is not None:
            display.change_status("Feeds successfully reloaded")
            display.menus_valid = False
