import os
import json
from castero.datafile import DataFile
from castero.feed import Feed
from castero.episode import Episode


class FeedsError(Exception):
    """An ambiguous error while handling the feeds.
    """


class Feeds(DataFile):
    """The Feeds class.

    Reads and stores information about the user's feeds. Instances of this
    class can generally be treated like dictionaries, accessing a feed with
    feeds_instance[feed_key].

    The feed_key for a feed is either the feed's file path or URL, which each
    feed object is ensured to have exactly one of.
    """
    PATH = os.path.join(DataFile.DATA_DIR, 'feeds')
    DEFAULT_PATH = os.path.join(DataFile.PACKAGE, 'templates/feeds')

    def __init__(self) -> None:
        """Initializes the object.
        """
        super().__init__(self.PATH, self.DEFAULT_PATH)
        self.load()

    def load(self) -> None:
        """Loads the feeds file.
        """
        assert os.path.exists(self._path)

        with open(self._path, 'r') as f:
            # any case of duplicate feed keys will be replaced with the first
            # occurrence of that key
            content = json.loads(f.read())

        for key in content:
            feed_dict = content[key]

            # assume urls start with http (change later?)
            if key.startswith('http'):
                # create feed from url
                feed = Feed(
                    url=key,
                    title=feed_dict["title"],
                    description=feed_dict["description"],
                    link=feed_dict["link"],
                    last_build_date=feed_dict["last_build_date"],
                    copyright=feed_dict["copyright"],
                    episodes=[],
                )
            else:
                # create feed from file
                feed = Feed(
                    file=key,
                    title=feed_dict["title"],
                    description=feed_dict["description"],
                    link=feed_dict["link"],
                    last_build_date=feed_dict["last_build_date"],
                    copyright=feed_dict["copyright"],
                    episodes=[],
                )

            episodes = [
                Episode(
                    feed,
                    title=episode_dict["title"],
                    description=episode_dict["description"],
                    link=episode_dict["link"],
                    pubdate=episode_dict["pubdate"],
                    copyright=episode_dict["copyright"],
                    enclosure=episode_dict["enclosure"]
                )
                for episode_dict in feed_dict["episodes"]
            ]

            for episode in episodes:
                feed.episodes.append(episode)

            # add feed to data
            self.data[key] = feed

    def write(self) -> None:
        """Writes to the data file.
        """
        assert os.path.exists(self._path)

        output_dict = dict(self.data)  # make a copy of self.data
        for key in output_dict:
            feed = output_dict[key]
            output_dict[key] = {
                "title": feed.title,
                "description": feed.description,
                "link": feed.link,
                "last_build_date": feed.last_build_date,
                "copyright": feed.copyright,
                "episodes": [
                    {
                        "title": episode.title,
                        "description": episode.description,
                        "link": episode.link,
                        "pubdate": episode.pubdate,
                        "copyright": episode.copyright,
                        "enclosure": episode.enclosure
                    }
                    for episode in feed.episodes
                ]
            }

        output = json.dumps(output_dict, indent=4)
        with open(self._path, 'w') as f:
            f.write(output)

    def reload(self, display=None) -> None:
        """Reloads feeds from their source to update properties/episodes.

        This method automatically calls write() after reloading the feeds.

        Args:
            display: (optional) the display to write status updates to
        """
        total_feeds = len(self.data)
        current_feed = 1
        for key in self.data:
            if display is not None:
                display.change_status(
                    "Reloading feeds (%d/%d)" % (current_feed, total_feeds)
                )

            # assume urls start with http (change later?)
            if key.startswith('http'):
                feed = Feed(url=key)
            else:
                feed = Feed(file=key)
            self.data[key] = feed
            current_feed += 1
        self.write()

        if display is not None:
            display.change_status("Feeds successfully reloaded")
            display.create_menus()

    def at(self, index) -> Feed:
        """Return the Feed at index.

        Args:
            index: the index of the Feed to retrieve

        Returns:
            Feed: the feed at the index
        """
        result = None
        if index < len(list(self.data)) > 0:
            result = self.data[list(self.data)[index]]
        return result

    def del_at(self, index) -> bool:
        """Deletes the Feed at index.

        Args:
            index: the index of the Feed to delete

        Returns:
            bool: whether a Feed was deleted
        """
        result = False
        if index < len(list(self.data)) > 0:
            result = True
            feed = self.data[list(self.data)[index]]
            for episode in feed.episodes:
                episode.delete()
            del self.data[list(self.data)[index]]
        return result
