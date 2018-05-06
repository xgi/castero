import os
import requests
from shutil import copyfile
import castero


class DataFile:
    """The DataFile class.

    Used when handling files with data that can reasonably be stored in a
    dictionary. Particularly used in the Config class and the Feeds class.

    Extended by classes which are based on a data file.
    """
    PACKAGE = os.path.dirname(__file__)
    HOME = os.path.expanduser('~')
    XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME',
                                os.path.join(HOME, '.config'))
    XDG_DATA_HOME = os.getenv('XDG_DATA_HOME',
                              os.path.join(HOME, '.local', 'share'))
    CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, castero.__title__)
    DATA_DIR = os.path.join(XDG_DATA_HOME, castero.__title__)
    DOWNLOADED_DIR = os.path.join(DATA_DIR, "downloaded")

    def __init__(self, path, default_path) -> None:
        """Initializes the object.

        Args:
            path: the path to the data file
            default_path: the path to the default data file
        """
        assert os.path.exists(default_path)

        self.data = {}
        self._path = path
        self._default_path = default_path

        # if path doesn't exit, create it based on default_path
        if not os.path.exists(self._path):
            DataFile.ensure_path(self._path)
            copyfile(self._default_path, self._path)

    def __iter__(self) -> iter:
        """Iterator for the keys of self.data

        In order to iterate over data values, you should use something like:
        for key in file_instance:
            value = file_instance[key]
        """
        return self.data.__iter__()

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, item):
        if item in self.data:
            return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        self.data.pop(key, None)

    @staticmethod
    def ensure_path(filename):
        """Ensure that the path to the filename exists, creating it if needed.
        """
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def download_to_file(url, file, name, download_queue, display=None):
        """Downloads a URL to a local file.

        Args:
            url: the source url
            file: the destination path
            name: the user-friendly name of the content
            download_queue: the download_queue overseeing this download
            display: (optional) the display to write status updates to
        """
        chunk_size = 1024
        chuck_size_label = "KB"

        response = requests.get(url, stream=True)
        handle = open(file, "wb")
        downloaded = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if display is not None:
                status_str = "Downloading \"%s\": %d%s" % (
                    name, downloaded / chunk_size, chuck_size_label
                )
                if download_queue.length > 1:
                    status_str += " (+%d downloads in queue)" % (
                        download_queue.length - 1
                    )

                display.change_status(status_str)
            if chunk:
                handle.write(chunk)
            downloaded += len(chunk)

        if display is not None:
            display.change_status("Episode successfully downloaded.")
        download_queue.next()

    def load(self) -> None:
        """Loads the data file.

        Should be implemented by classes which extend this class.
        """
        pass

    def write(self) -> None:
        """Writes to the data file.

        Should be implemented by classes which extend this class.
        """
        pass
