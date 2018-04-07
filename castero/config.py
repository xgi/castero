import os
import configparser
from castero.datafile import DataFile


class ConfigError(Exception):
    """An ambiguous error while handling the configuration.
    """


class ConfigParseError(ConfigError):
    """An error occurred while parsing the config file.
    """


class ConfigDuplicateError(ConfigError):
    """The config file contained a duplicate variable.
    """


class ConfigIncompleteError(ConfigError):
    """The config file did not contain all of the required variables.
    """


class ConfigExcessiveError(ConfigError):
    """The config file contained more than the default required variables.
    """


class Config(DataFile):
    """The Config class.

    Reads the configuration file. Instances of this class can generally be
    treated like dictionaries, accessing a variable with config_instance[key].

    Modifying config variables inside the application is not supported; config
    changes must be made to the config file itself.
    """
    PATH = os.path.join(DataFile.XDG_CONFIG_HOME, 'castero', 'castero.conf')
    DEFAULT_PATH = os.path.join(DataFile.PACKAGE, 'templates/castero.conf')

    def __init__(self) -> None:
        """Initializes the object.
        """
        super().__init__(self.PATH, self.DEFAULT_PATH)
        self.load()

    def __setitem__(self, key, value):
        pass

    def load(self) -> None:
        """Loads the config file.
        """
        assert os.path.exists(self._path)
        assert os.path.exists(self._default_path)

        conf = configparser.ConfigParser()
        try:
            conf.read(self._path)
        except configparser.ParsingError:
            raise ConfigParseError(
                "An error occurred while parsing the config file"
            )

        # we also read from the the default_conf to make sure conf contains
        # all of the necessary parameters
        default_conf = configparser.ConfigParser()
        try:
            default_conf.read(self._default_path)
        except configparser.ParsingError:
            raise ConfigParseError(
                "An error occurred while parsing the default config file"
                " (don't modify that one!)"
            )

        for section in conf:
            for key in conf[section]:
                if key in default_conf[section]:
                    # sections in the config file are purely for aesthetic
                    # purposes - this config object only stores variables
                    # at a single depth
                    if key in self.data:
                        raise ConfigDuplicateError(
                            "Variable defined multiple times, key: " + key
                        )

                    self.data[key] = conf[section][key]
                else:
                    # disallow keys which are not in the default config
                    raise ConfigExcessiveError(
                        "Unrecognized config variable, key: " + key
                    )

        # ensure that all variables in the default_conf are present
        for section in default_conf:
            for key in default_conf[section]:
                if key not in self.data.keys():
                    raise ConfigIncompleteError(
                        "Missing a config variable, key: " + key
                    )

