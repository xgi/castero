import json
import os
import sqlite3

from castero.datafile import DataFile
from castero.episode import Episode
from castero.feed import Feed


class FeedsDB():
    PATH = os.path.join(DataFile.DATA_DIR, 'feeds.db')
    SCHEMA = os.path.join(DataFile.PACKAGE, 'templates/feeds.schema')

    def __init__(self):
        existed = os.path.exists(self.PATH)
        self._conn = sqlite3.connect(self.PATH)

        if not existed:
            with open(self.SCHEMA, 'rt') as f:
                schema = f.read()
            self._conn.executescript(schema)
            self._migrate_from_old_feeds()

    def _migrate_from_old_feeds(self):
        path = os.path.join(DataFile.DATA_DIR, 'feeds')

        with open(path, 'r') as f:
            content = json.loads(f.read())

        for key in content:
            feed_dict = content[key]
            
            sql = "insert into feed (title, description, link, last_build_date, copyright)\n" \
                  "values (?,?,?,?,?)"
            self._conn.execute(sql, (
                feed_dict["title"],
                feed_dict["description"],
                feed_dict["link"],
                feed_dict["last_build_date"],
                feed_dict["copyright"]
            ))

            for episode_dict in feed_dict["episodes"]:
                sql = "insert into episode (title, feed, description, link, pubdate, copyright, enclosure)\n" \
                      "values (?,?,?,?,?,?,?)"
                self._conn.execute(sql, (
                    episode_dict["description"] if episode_dict["title"] == "" else episode_dict["title"],
                    episode_dict["title"],
                    feed_dict["title"],
                    episode_dict["description"],
                    episode_dict["link"],
                    episode_dict["pubdate"],
                    episode_dict["copyright"],
                    episode_dict["enclosure"]
                ))

        self._conn.commit()
