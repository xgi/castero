class Episode:
    """The Episode class.

    This class represents a single episode from a podcast feed.
    """
    def __init__(self, title=None, description=None, link=None,
                 pubdate=None, copyright=None, enclosure=None) -> None:
        """Initializes the object.

        At least one of a title or description must be specified.

        Args:
            title: (optional) the title of the episode
            description: (optional) the description of the episode
            link: (optional) a link to the episode
            pubdate: (optional) the date the episode was published, as a string
            copyright: (optional) the copyright notice of the episode
            enclosure: (optional) a url to a media file
        """
        assert title is not None or description is not None

        self._title = title
        self._description = description
        self._link = link
        self._pubdate = pubdate
        self._copyright = copyright
        self._enclosure = enclosure

    def __str__(self) -> str:
        """Represent this object as a single-line string.

        Returns:
            string: this episode's title, if it exists, else its description
        """
        if self._title is not None:
            representation = self._title
        else:
            representation = self._description
        return representation.split('\n')[0]

    @property
    def title(self) -> str:
        result = self._title
        if result is None:
            result = "Title not available."
        return result

    @property
    def description(self) -> str:
        result = self._description
        if result is None:
            result = "Description not available."
        return result

    @property
    def link(self) -> str:
        result = self._link
        if result is None:
            result = "Link not available."
        return result

    @property
    def pubdate(self) -> str:
        result = self._pubdate
        if result is None:
            result = "Publish date not available."
        return result

    @property
    def copyright(self) -> str:
        result = self._copyright
        if result is None:
            result = "Copyright not available."
        return result

    @property
    def enclosure(self) -> str:
        result = self._enclosure
        if result is None:
            result = "Enclosure not available."
        return result
