import json
import os
import sqlite3
from typing import List

from castero.datafile import DataFile
from castero.episode import Episode
from castero.feed import Feed


class FeedsDB():
    PATH = os.path.join(DataFile.DATA_DIR, 'feeds.db')
    SCHEMA = os.path.join(DataFile.PACKAGE, 'templates/feeds.schema')

    def __init__(self):
        existed = os.path.exists(self.PATH)
        self._conn = sqlite3.connect(self.PATH)
        self._cursor = self._conn.cursor()

        if not existed:
            with open(self.SCHEMA, 'rt') as f:
                schema = f.read()
            self._cursor.executescript(schema)
            self._migrate_from_old_feeds()

    def _migrate_from_old_feeds(self):
        path = os.path.join(DataFile.DATA_DIR, 'feeds')

        with open(path, 'r') as f:
            content = json.loads(f.read())

        for key in content:
            feed_dict = content[key]

            sql = "insert into feed (key, title, description, link, last_build_date, copyright)\n" \
                  "values (?,?,?,?,?,?)"
            self._cursor.execute(sql, (
                key,
                feed_dict["title"],
                feed_dict["description"],
                feed_dict["link"],
                feed_dict["last_build_date"],
                feed_dict["copyright"]
            ))

            for episode_dict in feed_dict["episodes"]:
                sql = "insert into episode (key, title, feed, description, link, pubdate, copyright, enclosure)\n" \
                      "values (?,?,?,?,?,?,?,?)"
                self._cursor.execute(sql, (
                    episode_dict["description"] if episode_dict["title"] == "" else episode_dict["title"],
                    episode_dict["title"],
                    key,
                    episode_dict["description"],
                    episode_dict["link"],
                    episode_dict["pubdate"],
                    episode_dict["copyright"],
                    episode_dict["enclosure"]
                ))

        self._conn.commit()

    def replace_feed(self, feed: Feed) -> None:
        sql = "replace into feed (key, title, description, link, last_build_date, copyright)\n" \
              "values (?,?,?,?,?,?)"
        self._cursor.execute(sql, (
            feed.key,
            feed.title,
            feed.description,
            feed.link,
            feed.last_build_date,
            feed.copyright
        ))
        self._conn.commit()

    def replace_episode(self, feed: Feed, episode: Episode) -> None:
        sql = "replace into episode (key, title, feed, description, link, pubdate, copyright, enclosure)\n" \
              "values (?,?,?,?,?,?,?,?)"
        self._cursor.execute(sql, (
            episode.key,
            episode.title,
            feed.key,
            episode.description,
            episode.link,
            episode.pubdate,
            episode.copyright,
            episode.enclosure
        ))
        self._conn.commit()

    @property
    def feeds(self) -> List[Feed]:
        sql = "select key, title, description, link, last_build_date, copyright from feed"
        self._cursor.execute(sql)

        feeds = []
        for row in self._cursor.fetchall():
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

    @property
    def episodes(self, feed: Feed) -> List[Episode]:
        sql = "select title, description, link, pubdate, copyright, enclosure from episode where feed=?"
        self._cursor.execute(sql, (feed.key,))

        episodes = []
        for row in self._cursor.fetchall():
            episodes.append(Episode(
                feed,
                title=row[0],
                description=row[1],
                link=row[2],
                pubdate=row[3],
                copyright=row[4],
                enclosure=row[5]
            ))
        return episodes
