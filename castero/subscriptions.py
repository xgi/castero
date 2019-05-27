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
        file = None
        try:
            file = open(path)
            text = file.read()
            try:
                self._tree = ElementTree.fromstring(text)
            except ElementTree.ParseError:
                raise SubscriptionsParseError(
                    "Unable to parse text as an XML document")
        except IOError:
            raise SubscriptionsLoadError(
                "An exception occurred when attempting to load the file")
        finally:
            if file is not None:
                file.close()

        body = self._tree.find('body')
        container = body.find('outline')
        entries = container.findall('outline')
        for entry in entries:
            feed = Feed(url=entry.attrib['xmlUrl'])
