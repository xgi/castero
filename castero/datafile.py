import os
from shutil import copyfile


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
