import requests
import xml.etree.ElementTree as ElementTree
from castero.episode import Episode


class FeedError(Exception):
    """An ambiguous error while handling the feed.
    """


class FeedLoadError(FeedError):
    """A feed could not be found at the provided file, or an IO exception
    occurred when loading the file.
    """


class FeedDownloadError(FeedError):
    """A feed could not be found at the provided URL, or a request exception
    occurred when downloading the feed.
    """


class FeedParseError(FeedError):
    """The document at the provided URL could not be parsed as an XML document.
    """


class FeedStructureError(FeedError):
    """The feed at the provided URL is not a properly structured RSS document.
    """


class Feed:
    """The Feed class.

    This class uses a provided url to retrieve all data and metadata for a
    podcast feed. It creates and is a parent to all episode objects which are
    available on the feed.

    The url for the feed should point to an RSS document.
    """
    def __init__(self, url=None, file=None, **kwargs) -> None:
        """Initializes the object.

        A feed can be provided as either a url or a file, but exactly one must
        be given. Realistically, users will almost universally use a url to
        retrieve feeds from. However, having support for handling files makes
        testing easier.

        Args:
            url: (optional) the url where the feed is located
            file: (optional) the file where the feed is located
        """
        # * Don't allow providing both a url and a file, but must provide one.
        # Check that one of them is None, and that they are not both the same.
        # The second conditional can be read as checking that both variables
        # are not None.
        assert (url is None or file is None) and (url is not file)

        self._url = url
        self._file = file
        self._tree = None
        self._validated = False

        self._title = kwargs.get('title', None)
        self._description = kwargs.get('description', None)
        self._link = kwargs.get('link', None)
        self._last_build_date = kwargs.get('last_build_date', None)
        self._copyright = kwargs.get('copyright', None)
        self._episodes = kwargs.get('episodes', [])

        # assume that if we have been passed the title then we have also been
        # passed everything else and that the feed is valid
        if self._title is None:
            # retrieve the feed and parse to XML document
            self._download_feed()
            # check that the XML document is a properly structured RSS feed
            self._validate_feed()
            # set this object's metadata using rss feed, and creates episodes
            self._process_feed()
        else:
            self._validated = True

    def __str__(self) -> str:
        """Represent this object as a string.

        Returns:
            string: this feed's title
        """
        assert self._title is not None

        return self._title

    def _download_feed(self):
        """Parses the feed at the provided url or file into _tree.

        This method checks whether the url is valid and that there is a
        parse-able XML document at the url, but it does not check that the
        document is an RSS feed, nor whether the feed has all necessary tags.

        Raises:
            FeedParseError: unable to parse text as an XML document
            FeedDownloadError: (only when retrieving feed using url) did not
                receive an acceptable status code, or an exception occurred
                when attempting to download the page
            FeedLoadError: (only when retrieving feed using file) a feed could
                not be found at the file, or an exception occurred when
                attempting to load the file
        """
        if self._url is not None:
            # handle feed from url
            try:
                response = requests.get(self._url)
                if response.status_code == 200:
                    try:
                        self._tree = ElementTree.fromstring(response.text)
                    except ElementTree.ParseError:
                        raise FeedParseError(
                            "Unable to parse text as an XML document")
                else:
                    raise FeedDownloadError(
                        "Did not receive an acceptable status code while"
                        " download the page. Expected 200, got: " +
                        str(response.status_code))
            except requests.exceptions.RequestException:
                raise FeedDownloadError(
                    "An exception occurred when attempting to download the"
                    " page")
        elif self._file is not None:
            # handle feed from file
            file = None
            try:
                file = open(self._file)
                text = file.read()
                try:
                    self._tree = ElementTree.fromstring(text)
                except ElementTree.ParseError:
                    raise FeedParseError(
                        "Unable to parse text as an XML document")
            except IOError:
                raise FeedLoadError(
                    "An exception occurred when attempting to load the file")
            finally:
                if file is not None:
                    file.close()

    def _validate_feed(self):
        """Checks that the provided XML document is a valid RSS feed.

        This method is intended to be run only when this object is being
        created in order to raise any necessary exceptions at that time.

        The conditions check are:
            - the root of the XML document is an 'rss' tag
            - the root has a 'version' attribute which equals '2.0'
            - the root has exactly one child, which is the channel tag
            - the channel tag has at least 3 children, which include a title,
              link, and description tag (in any order)
            - for each child of the channel tag which is an item tag, if any:
                - the item tag must have at least one child, which is a title
                  tag or a description tag
        See http://cyber.harvard.edu/rss/rss.html for more details.

        This method does not set this object's metadata. That is done in
        _process_feed().

        Raises:
            FeedStructureError: the XML document violates one of the conditions
        """
        assert self._tree is not None

        # root should be an rss tag
        if self._tree.tag != 'rss':
            raise FeedStructureError("XML document is not an RSS feed")

        # root should have version attribute which equals 2.0
        if 'version' in self._tree.attrib:
            if self._tree.attrib['version'] != '2.0':
                raise FeedStructureError("RSS version is not 2.0")
        else:
            raise FeedStructureError(
                "RSS feed does not have a version attribute")

        # root should have one child, which is the channel tag
        root_children = self._tree.getchildren()
        if len(root_children) > 0:
            if len(root_children) > 1:
                raise FeedStructureError(
                    "RSS feed has too many children; expected 1, was: " +
                    str(len(root_children)))
            else:
                if root_children[0].tag != 'channel':
                    raise FeedStructureError(
                        "RSS feed does not have a channel tag as its child")
                else:
                    # channel should have at least 3 children, including a
                    # title, link, and description tag
                    channel = root_children[0]
                    channel_children = channel.getchildren()
                    if len(channel_children) >= 3:
                        chan_title_tags = channel.findall('title')
                        chan_link_tags = channel.findall('link')
                        chan_description_tags = channel.findall('description')

                        if len(chan_title_tags) != 1:
                            raise FeedStructureError(
                                "RSS feed's channel has too many or too few"
                                " title tags; expected 1, was: " +
                                str(len(chan_title_tags)))
                        if len(chan_link_tags) != 1:
                            raise FeedStructureError(
                                "RSS feed's channel has too many or too few"
                                " link tags; expected 1, was: " +
                                str(len(chan_link_tags)))
                        if len(chan_description_tags) != 1:
                            raise FeedStructureError(
                                "RSS feed's channel has too many or too few"
                                " description tags; expected 1, was: " +
                                str(len(chan_description_tags)))

                        # if the channel has any items, each item should have
                        # at least a title or description tag
                        channel_item_tags = channel.findall('item')
                        for item in channel_item_tags:
                            if len(item.findall('title') +
                                   item.findall('description')) < 1:
                                raise FeedStructureError(
                                    "An item in the RSS feed's channel did not"
                                    " have at least one of a title or a"
                                    " description tag")
                    else:
                        raise FeedStructureError(
                            "RSS feed's channel does not have enough required"
                            " children; expected >=3, was: " +
                            str(len(channel_children)))
        else:
            raise FeedStructureError(
                "RSS feed does not have any children; expected 1 (a channel"
                " tag)")

        self._validated = True

    def _process_feed(self):
        """Processes the RSS feed to set metadata and create episodes.

        It is required that _validate_feed be run prior to running this method.
        """
        assert self._validated

        channel = self._tree.getchildren()[0]
        self._title = channel.find('title').text
        self._description = channel.find('description').text
        self._link = channel.find('link').text

        last_build_date_tag = channel.find('lastBuildDate')
        copyright_tag = channel.find('copyright')

        if last_build_date_tag is not None:
            self._last_build_date = last_build_date_tag.text
        if copyright_tag is not None:
            self._copyright = copyright_tag.text

        # process items into episodes
        for item in channel.findall('item'):
            item_title = item.find('title')
            item_description = item.find('description')
            item_link = item.find('link')
            item_pubdate = item.find('pubDate')
            item_copyright = item.find('copyright')
            item_enclosure = item.find('enclosure')

            item_title_str = None
            item_description_str = None
            item_link_str = None
            item_pubdate_str = None
            item_copyright_str = None
            item_enclosure_str = None

            if item_title is not None:
                item_title_str = item_title.text
            if item_description is not None:
                item_description_str = item_description.text
            if item_link is not None:
                item_link_str = item_link.text
            if item_pubdate is not None:
                item_pubdate_str = item_pubdate.text
            if item_copyright is not None:
                item_copyright_str = item_copyright.text
            if item_enclosure is not None:
                if 'url' in item_enclosure.attrib.keys():
                    item_enclosure_str = item_enclosure.attrib['url']

            episode = Episode(self,
                              title=item_title_str,
                              description=item_description_str,
                              link=item_link_str,
                              pubdate=item_pubdate_str,
                              copyright=item_copyright_str,
                              enclosure=item_enclosure_str)
            self._episodes.append(episode)

    @property
    def validated(self) -> bool:
        """bool: whether this feed has been validated"""
        return self._validated

    @property
    def title(self) -> str:
        """str: the title of the feed"""
        return self._title

    @property
    def description(self) -> str:
        """str: the description of the feed"""
        return self._description

    @property
    def episodes(self) -> list:
        """list: a list of this feed's castero.episode.Episode's"""
        return self._episodes

    @property
    def link(self) -> str:
        """str: the link of/for the feed"""
        result = self._link
        if result is None:
            result = "Link not available."
        return result

    @property
    def last_build_date(self) -> str:
        """str: the last build date of the feed"""
        result = self._last_build_date
        if result is None:
            result = "Last build date not available."
        return result

    @property
    def copyright(self) -> str:
        """str: the copyright of the feed"""
        result = self._copyright
        if result is None:
            result = "No copyright specified."
        return result
