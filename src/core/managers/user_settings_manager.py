import json
import os
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from core import paths
from core.logging.logging_system import Logger


class UserSettingsManager(EventDispatcher):
    """
    This class manages user settings e.g. if an open dust shoe should be detected or not.
    All settings:
     - will be saved into user_settings.json and loaded on startup.
     - are defined as kivy properties

    Settings have
     - a name: str (used for internal usage in code, key of the dict entry)
     - a title: str (used for title labels e.g. settings tab)
     - a description: str (used for descriptive labels)
     - a value: corresponding to their specific type

     This settings manager provides getters and setters. Setters will do a validation check.

     Create new settings:
     Just add the new setting to the settings dictionary

     Usage:

     DON'T INSTANTIATE YOURSELF! GET IT FROM THE APP!
     user_settings_manager = App.get_running_app().user_settings_manager

     my_bool_attribute = user_settings_manager.get_value('dust_shoe_detection')
     user_settings_manager.set_value('dust_shoe_detection', value)
     my_title_label.text = user_settings_manager.get_title('dust_shoe_detection')
     my_description_label.text = user_settings_manager.get_description('dust_shoe_detection')
    """

    SETTINGS_FILE_PATH = os.path.join(paths.SB_VALUES_PATH, "user_settings.json")
    settings = {
        "dust_shoe_detection": {
            "description": "When activated, the dust shoe needs to be inserted when starting the spindle or running jobs.",
            "title": "Dust shoe plug detection",
            "value": True,
        },
        "interrupt_bars_active": {
            "description": "When activated, hitting the interrupt bars will trigger an alarm! Only deactivate this if your interrupt bar switches are broken!",
            "title": "Interrupt bars activated",
            "value": True,
        },
    }
    for name, details in settings.items():
        if type(details["value"]) == bool:
            vars()[name] = BooleanProperty(details["value"])
        elif type(details["value"]) == str:
            vars()[name] = StringProperty(details["value"])
        elif type(details["value"]) == float:
            vars()[name] = NumericProperty(details["value"])

    def __init__(self, **kwargs):
        Logger.info("Creating new instance of UserSettingsManager")
        self.load_settings_from_file()
        super().__init__(**kwargs)

    def load_settings_from_file(self):
        """Loads the settings from the file and update the local dictionary."""
        if os.path.exists(self.SETTINGS_FILE_PATH):
            with open(self.SETTINGS_FILE_PATH) as f:
                Logger.info(f"Loading settings from file: {self.SETTINGS_FILE_PATH}")
                tmp = json.load(f)
                self.settings.update(tmp)
            for name, details in self.settings.items():
                setattr(self, name, details["value"])

    def save_settings_to_file(self):
        """Saves the local settings dictionary to a file."""
        with open(self.SETTINGS_FILE_PATH, "w") as f:
            Logger.info(f"Updating file: {self.SETTINGS_FILE_PATH}")
            json.dump(self.settings, f, sort_keys=True, indent=4)

    def get_value(self, settings_name):
        """Returns the value of the given settings_name. If no such setting exists a KeyError is raised."""
        return self.settings[settings_name]["value"]

    def get_type(self, settings_name):
        """Returns the type of the given settings_name. If no such setting exists a KeyError is raised."""
        return type(self.settings[settings_name]["value"])

    def get_description(self, settings_name):
        """Returns the description of the given settings_name. If no such setting exists a KeyError is raised."""
        return self.settings[settings_name]["description"]

    def get_title(self, settings_name):
        """Returns the title of the given settings_name. If no such setting exists a KeyError is raised."""
        return self.settings[settings_name]["title"]

    def set_value(self, settings_name, value):
        """
        Updates the value for the give setting and saves it to the file.
        If the setting does not exist, a KeyError is raised.
        If the value has the wrong type a ValueError is raised.
        """
        if type(self.settings[settings_name]["value"]) is not type(value):
            Logger.error(
                "Wrong value type! Expected: {} | Received: {}".format(
                    type(self.settings[settings_name]["value"]), type(value)
                )
            )
            raise ValueError
        if self.settings[settings_name]["value"] != value:
            Logger.debug(f'new value for "{settings_name}": {value}')
            self.settings[settings_name]["value"] = value
            setattr(self, settings_name, value)
            self.save_settings_to_file()
