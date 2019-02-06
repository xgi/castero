import configparser
import os
import sys

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


class _Config(DataFile):
    """The Config class.

    Reads the configuration file. Instances of this class can generally be
    treated like dictionaries, accessing a variable with config_instance[key].

    Modifying config variables inside the application is not supported; config
    changes must be made to the config file itself.
    """
    PATH = os.path.join(DataFile.CONFIG_DIR, 'castero.conf')
    DEFAULT_PATH = os.path.join(DataFile.PACKAGE, 'templates/castero.conf')

    def __init__(self) -> None:
        """Initializes the object.
        """
        super().__init__(self.PATH, self.DEFAULT_PATH)

        # strictly use default path when testing
        if "pytest" in sys.modules:
            self._path = self._default_path

        self.load()

    def __setitem__(self, key, value):
        pass

    def load(self) -> None:
        """Loads the config file.

        Raises:
            ConfigParseError: an error occurred while parsing the config file
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

        # ensure that all variables in the default_conf are present
        for section in default_conf:
            if section not in conf:
                self.migrate(conf, default_conf)
                break  # we will only ever need to migrate once
            for key in default_conf[section]:
                if key not in conf[section]:
                    self.migrate(conf, default_conf)
                    break  # we will only ever need to migrate once

        for section in conf:
            for key in conf[section]:
                if section in default_conf:
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
                        self.migrate(conf, default_conf)
                else:
                    self.migrate(conf, default_conf)

    def migrate(self, conf, default_conf) -> None:
        """Migrates the user's config to have the same keys as the default.

        Generally this method will be used when the client is updated to change
        some parts of the default config.

        The migration process is rather brash -- it simply retains the user's
        current config in memory, overwrites their file with the default file,
        and then using basic parsing replaces any variables already defined
        by the user with their definition.

        Args:
            conf: ConfigParser of the user's config file
            default_conf: ConfigParser of the default config file
        """
        # convert conf and default_conf to 1-dim dictionaries since they may
        # not have the same sections
        conf_dict = {}
        for section in conf:
            for key in conf[section]:
                conf_dict[key] = conf[section][key]
        default_conf_dict = {}
        for section in default_conf:
            for key in default_conf[section]:
                default_conf_dict[key] = default_conf[section][key]

        with open(self._default_path, "r") as default_conf_file:
            lines = default_conf_file.readlines()
            for line in lines:
                for key in default_conf_dict:
                    if line.startswith(key + " "):
                        if key in conf_dict:
                            lines[lines.index(line)] = "%s = %s\n" % (
                                line.split(" =")[0],
                                conf_dict[key]
                            )

        with open(self._path, "w") as conf_file:
            for line in lines:
                conf_file.write(line)
        conf.read(self._path)


Config = _Config()
