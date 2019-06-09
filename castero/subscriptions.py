import xml.etree.ElementTree as ElementTree
from typing import List

from castero.feed import Feed


class SubscriptionsError(Exception):
    """An ambiguous error while handling the document.
    """


class SubscriptionsLoadError(SubscriptionsError):
    """A document could not be found at the provided file, or an IO exception
    occurred when loading the file.
    """


class SubscriptionsParseError(SubscriptionsError):
    """The document could not be parsed as an XML document.
    """


class SubscriptionsStructureError(SubscriptionsError):
    """The file data is not a properly structured OPML document.
    """


class Subscriptions():
    """The Subscriptions class.

    Instances of this class represent a list of podcast subscriptions, which
    the user can import from (and export to) OPML-formatted documents.
    """

    def __init__(self) -> None:
        """Initializes the object.
        """
        self._tree = None
        self._feeds = []

    def load(self, path: str) -> None:
        """Load an OPML file of subscriptions.

        Args:
            path: the location of the OPML file to load

        Raises:
            SubscriptionsParseError: unable to parse text as an XML document
            SubscriptionsLoadError: an exception occurred when attempting to
                load the file
            SubscriptionsStructureError: the file data is not a properly
                structured OPML document
        """
        self._tree = None
        try:
            self._tree = ElementTree.parse(path)
            self._parse_feeds()
        except IOError:
            raise SubscriptionsLoadError(
                "An I/O exception occurred when attempting to load the file")
        except ElementTree.ParseError:
            raise SubscriptionsParseError(
                "Unable to parse text as an XML document")

    def save(self, path: str) -> None:
        """Save an OPML file of subscriptions.

        A subscriptions document must have been loaded (with .load) or created
        (with .generate) before running this method.

        Args:
            path: the location of the OPML file to create

        Raises:
            SubscriptionsError: attempted to save before creating document
            SubscriptionsLoadError: an exception occurred when attempting to
                write the file
        """
        if self._tree is not None:
            try:
                self._tree.write(path, xml_declaration=True)
            except IOError:
                raise SubscriptionsLoadError(
                    "An I/O exception occurred when attempting to save the"
                    " file")
        else:
            raise SubscriptionsError(
                "Attempted to save an XML document that has not been loaded or"
                " created")

    def generate(self, feeds: List[Feed]) -> None:
        """Create subscriptions document from list of feeds.

        Args:
            feeds: the list of feeds to include in the document
        """
        builder = ElementTree.TreeBuilder()

        builder.start("opml", {'version': '1.0'})
        builder.start("head", {})
        builder.start("title", {})
        builder.data("castero feeds")
        builder.end("title")
        builder.end("head")
        builder.start("body", {})
        builder.start("outline", {'text': 'feeds'})
        for feed in feeds:
            builder.start("outline", {
                'type': 'rss',
                'text': str(feed),
                'xmlUrl': feed.key
            })
            builder.end("outline")
        builder.end("outline")
        builder.end("body")
        builder.end("opml")

        # .close returns an Element, so we need to cast to an ElementTree
        self._tree = ElementTree.ElementTree(builder.close())

    def _parse_feeds(self) -> None:
        """Parse the XML tree into a list of feeds.

        Raises:
            SubscriptionsStructureError: the file data is not a properly
                structured OPML document
        """
        error_msg = "The file data is not a properly structured OPML document"

        if self._tree is None:
            raise SubscriptionsStructureError(error_msg)
        body = self._tree.find('body')
        if body is None:
            raise SubscriptionsStructureError(error_msg)
        container = body.find('outline')
        if container is None:
            raise SubscriptionsStructureError(error_msg)
        entries = container.findall('outline')
        if entries is None:
            raise SubscriptionsStructureError(error_msg)

        self._feeds = []
        for entry in entries:
            feed = Feed(url=entry.attrib['xmlUrl'])
            self._feeds.append(feed)

    @property
    def feeds(self) -> List[Feed]:
        """List[Feed]: the loaded feeds"""
        return self._feeds
