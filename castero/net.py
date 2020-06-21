import castero
import requests
import grequests


class Net:
    """Manager for network requests.

    This class provides helper methods for network requests. Generally just a
    wrapper around the requests library.
    """
    USER_AGENT = "%s %s <%s>" % (
        castero.__title__, castero.__version__, castero.__url__)
    HEADERS = {
        'User-Agent': USER_AGENT
    }

    @staticmethod
    def Get(*args, **kwargs) -> requests.models.Response:
        """Send a GET request.

        Args:
            *args: arguments for requests.get(); particularly the URL
            **kwargs: optional arguments for requests.get()

        Returns:
            requests.models.Response: response
        """
        return requests.get(
            *args,
            headers=Net.HEADERS,
            timeout=float(castero.config.Config['request_timeout']),
            proxies={
                'http': castero.config.Config['proxy_http'],
                'https': castero.config.Config['proxy_https'],
            },
            **kwargs
        )

    @staticmethod
    def GGet(*args, **kwargs):
        return grequests.get(
            *args,
            headers=Net.HEADERS,
            timeout=float(castero.config.Config['request_timeout']),
            proxies={
                'http': castero.config.Config['proxy_http'],
                'https': castero.config.Config['proxy_https'],
            },
            **kwargs
        )
