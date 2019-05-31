import xml.etree.ElementTree as ElementTree

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

    def __init__(self):
        self._tree = None
        self._feeds = []

    def load(self, path):
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

    def save(self, path):
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

    def _parse_feeds(self):
        body = self._tree.find('body')
        container = body.find('outline')
        entries = container.findall('outline')

        self._feeds = []
        for entry in entries:
            feed = Feed(url=entry.attrib['xmlUrl'])
            self._feeds.append(feed)
