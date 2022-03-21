"""Make Zip v1.0.0"""

import os
import yaml
import zipfile


class MakeZip:

    """
    The main class of Makezip.\n
    Variable(s) stores inside object, containing:\n
    PATH(str), FILENAME(str), EXPORT_DIRECTORY(str)
    INCLUDE(list), EXCLUDE(list), CONSTRUCTOR(Construct)
    """

    PATH = None
    FILENAME = None
    EXPORT_DIRECTORY = None
    INCLUDE = []
    EXCLUDE = []
    CONSTRUCTOR = None

    class Construct:

        """
        The attached class of Makezip, implementing constructive usages.\n
        You shouldn't access to this class in any case.\n
        Variable(s) stores inside object, containing:\n
        REPLACEMENTS(dict)
        """

        REPLACEMENTS = {}

        @staticmethod
        def path(path: str = "", file: str = None) -> str:
            if str is None:
                raise TypeError
            return "{}/{}".format(path, file)

        @classmethod
        def directory(cls, path: str = ".") -> list:
            structure = os.listdir(path)
            for directory in [
                item for item in os.listdir(path) if os.path.isdir(cls.path(path, item))
            ]:
                structure += [
                    cls.path(directory, file)
                    for file in cls.directory(cls.path(path, directory))
                ]
            return structure

        def text(self, text: str) -> str:
            for key, value in self.REPLACEMENTS.items():
                text = text.replace(key, value)
            return text

        def __init__(self, REPLACEMENTS: dict = {}) -> None:
            self.REPLACEMENTS = REPLACEMENTS
            return

    def _loadConfig(self, PATH: str):

        """
        You shouldn't access to this method in any case.
        """

        with open(PATH, "r+") as file:
            CONFIG = yaml.safe_load(file)
        _ = self.CONSTRUCTOR.text
        self.FILENAME = _(CONFIG["FILENAME"])
        self.EXPORT_DIRECTORY = _(CONFIG["EXPORT_DIRECTORY"])
        self.INCLUDE = CONFIG["INCLUDE"]
        self.EXCLUDE = CONFIG["EXCLUDE"]

    def __init__(
        self,
        CONFIG: str = "makezip.config.yml",
        PATH: str = ".",
        CONSTRUCTOR_FUNCTION: object = lambda: {},
        *CONSTRUCTOR_ARGS,
        **CONSTRUCTOR_KWARGS
    ):
        self.CONSTRUCTOR = self.Construct(
            REPLACEMENTS=CONSTRUCTOR_FUNCTION(*CONSTRUCTOR_ARGS, **CONSTRUCTOR_KWARGS)
        )
        self._loadConfig(self.CONSTRUCTOR.path(PATH, CONFIG))
        self.PATH = PATH

    def make(self):
        # Declairs Construct methods.
        _, __, ___ = (
            self.CONSTRUCTOR.text,
            self.CONSTRUCTOR.directory,
            self.CONSTRUCTOR.path,
        )
        # Includes files.
        INCLUDE_TARGETS = []
        INCLUDE_TARGETS += [
            _(file) for file in self.INCLUDE["FILE"] if _(file) in __(self.PATH)
        ]
        for directory in [
            _(directory)
            for directory in self.INCLUDE["DIRECTORY"]
            if _(directory) in __(self.PATH)
        ]:
            INCLUDE_TARGETS += [
                _(file) for file in __(self.PATH) if _(file).startswith(directory)
            ]
        # Excludes files.
        EXCLUDE_TARGETS = []
        EXCLUDE_TARGETS += [
            _(file) for file in self.EXCLUDE["FILE"] if _(file) in __(self.PATH)
        ]
        for directory in [
            _(directory)
            for directory in self.EXCLUDE["DIRECTORY"]
            if _(directory) in __(self.PATH)
        ]:
            EXCLUDE_TARGETS += [
                _(file) for file in __(self.PATH) if _(file).startswith(directory)
            ]
        TARGETS = list(set(INCLUDE_TARGETS) - set(EXCLUDE_TARGETS))
        # Zips files.
        if not os.path.exists(___(self.PATH, self.EXPORT_DIRECTORY)):
            os.makedirs(___(self.PATH, self.EXPORT_DIRECTORY))
        with zipfile.ZipFile(
            ___(self.PATH, ___(self.EXPORT_DIRECTORY, self.FILENAME)), mode="w"
        ) as archive:
            for file in TARGETS:
                archive.write(file)
