import json
import os
import sqlite3
from typing import List, Tuple

from castero.datafile import DataFile
from castero.episode import Episode
from castero.feed import Feed


class Database():
    PATH = os.path.join(DataFile.DATA_DIR, 'castero.db')
    OLD_PATH = os.path.join(DataFile.DATA_DIR, 'feeds')
    SCHEMA = os.path.join(DataFile.PACKAGE, 'templates/feeds.schema')

    def __init__(self):
        existed = os.path.exists(self.PATH)
        self._conn = sqlite3.connect(self.PATH, check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")

        if not existed:
            with open(self.SCHEMA, 'rt') as f:
                schema = f.read()
            self._conn.cursor().executescript(schema)

            if os.path.exists(self.OLD_PATH):
                self._migrate_from_old_feeds()

    def _migrate_from_old_feeds(self):
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
        sql = "delete from feed where key=?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (feed.key,))
        self._conn.commit()

    def replace_feed(self, feed: Feed) -> None:
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
        cursor = self._conn.cursor()
        if episode.ep_id is None:
            sql = "replace into episode (title, feed_key, description, link, pubdate, copyright, enclosure)\n" \
                "values (?,?,?,?,?,?,?)"
            cursor.execute(sql, (
                episode.title,
                feed.key,
                episode.description,
                episode.link,
                episode.pubdate,
                episode.copyright,
                episode.enclosure
            ))
            episode.ep_id = cursor.lastrowid
        else:
            sql = "replace into episode (id, title, feed_key, description, link, pubdate, copyright, enclosure)\n" \
                "values (?,?,?,?,?,?,?,?)"

            cursor.execute(sql, (
                episode.ep_id,
                episode.title,
                feed.key,
                episode.description,
                episode.link,
                episode.pubdate,
                episode.copyright,
                episode.enclosure
            ))
        self._conn.commit()

    def replace_episodes(self, feed: Feed, episodes: List[Episode]) -> None:
        for episode in episodes:
            self.replace_episode(feed, episode)
        self._conn.commit()

    def feeds(self) -> List[Feed]:
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
                copyright=row[5],
                episodes=[],
            ))
        return feeds

    def episodes(self, feed: Feed) -> List[Episode]:
        sql = "select id, title, description, link, pubdate, copyright, enclosure from episode where feed_key=?"
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
                enclosure=row[6]
            ))
        return episodes

    def feed(self, key) -> Feed:
        sql = "select key, title, description, link, last_build_date, copyright from feed"
        cursor = self._conn.cursor()
        cursor.execute(sql)

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
        sql = "select feed_key, id, title, description, link, pubdate, copyright, enclosure from episode where id=?"
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
                enclosure=result[7]
            )

    def reload(self, display=None) -> None:
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

            self.replace_episodes(new_feed, self.episodes(new_feed))
            self.replace_feed(new_feed)

        if display is not None:
            display.change_status("Feeds successfully reloaded")
            display.create_menus()