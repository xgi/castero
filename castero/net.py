import castero
import requests


class Net:
    """The Net class.

    This class provides helper methods for network requests. Generally just a
    wrapper around the requests library.
    """
    USER_AGENT = "%s %s <%s>" % (
        castero.__title__, castero.__version__, castero.__url__)
    HEADERS = {
        'User-Agent': USER_AGENT
    }

    @staticmethod
    def Get(url, **kwargs) -> requests.models.Response:
        """Send a GET request.

        Args:
            url: URL to retrieve from
            **kwargs: optional arguments for requests.get()

        Returns:
            requests.models.Response: response
        """
        return requests.get(url, headers=Net.HEADERS, **kwargs)
