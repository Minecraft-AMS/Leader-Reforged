import json
import os
import yaml
import zipfile

class MakePlugin():

    PATH = None
    FILENAME = None
    EXPORT_DIRECTORY = None
    INCLUDE = [None]
    EXCLUDE = [None]
    PLUGIN_ID = None
    VERSION = None
    TARGETS = []
    
    @staticmethod
    def constructDirectory(path: str = "."):
        structure = os.listdir(path)
        for directory in [item for item in os.listdir(path) if os.path.isdir("{}/{}".format(path, item))]:
            structure += ["{}/{}".format(directory, file) for file in MakePlugin.constructDirectory("{}/{}".format(path, directory))]
        return structure
        
    def loadMetadata(self, path: str):
        with open(path, "r+") as file:
            METADATA = json.load(file)
        self.PLUGIN_ID = METADATA["id"]
        self.VERSION = METADATA["version"]

    def loadConfig(self, path: str):
        with open(path, "r+") as file:
            CONFIG = yaml.safe_load(file)
        self.FILENAME = CONFIG["FILENAME"].replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION)
        self.EXPORT_DIRECTORY = CONFIG["EXPORT_DIRECTORY"].replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION)
        self.INCLUDE = CONFIG["INCLUDE"]
        self.EXCLUDE = CONFIG["EXCLUDE"]

    def including(self):
        self.TARGETS += [file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) for file in self.INCLUDE["FILE"] if file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) in self.constructDirectory(self.PATH)]
        for directory in [directory.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) for directory in self.INCLUDE["DIRECTORY"] if directory.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) in self.constructDirectory(self.PATH)]:
            self.TARGETS += [file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) for file in self.constructDirectory(self.PATH) if file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION).startswith(directory)]
        self.TARGETS = list(set(self.TARGETS))

    def excluding(self):
        TARGETS = []
        TARGETS += [file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) for file in self.EXCLUDE["FILE"] if file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) in self.constructDirectory(self.PATH)]
        for directory in [directory.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) for directory in self.EXCLUDE["DIRECTORY"] if directory.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) in self.constructDirectory(self.PATH)]:
            self.TARGETS += [file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION) for file in self.constructDirectory(self.PATH) if file.replace("$PLUGIN_ID$", self.PLUGIN_ID).replace("$VERSION$", self.VERSION).startswith(directory)]
        self.TARGETS = list(set(self.TARGETS)-set(TARGETS))
    
    def zipping(self):
        if not os.path.exists("{}/{}".format(self.PATH, self.EXPORT_DIRECTORY)):
            os.makedirs("{}/{}".format(self.PATH, self.EXPORT_DIRECTORY))
        with zipfile.ZipFile("{}/{}/{}".format(self.PATH, self.EXPORT_DIRECTORY, self.FILENAME), mode="w") as archive:
            for file in self.TARGETS:
                archive.write(file)

    def __init__(self, METADATA: str = "mcdreforged.plugin.json", CONFIG: str = "makeplugin.config.yml", PATH: str = "."):
        self.loadMetadata("{}/{}".format(PATH, METADATA))
        self.loadConfig("{}/{}".format(PATH, CONFIG))
        self.PATH = PATH

    def make(self):
        self.including()
        self.excluding()
        self.zipping()

MakePlugin().make()