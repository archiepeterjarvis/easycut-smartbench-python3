import json
import os
import inspect
from kivy.app import App
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty
from apps.drywall_cutter_app.config import config_classes
from apps.drywall_cutter_app.config import config_options
from core.localization import Localization
from core.logging.logging_system import Logger
from core.managers.model_manager import ModelManagerSingleton

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIGURATIONS_DIR = os.path.join(CURRENT_DIR, "configurations")
MIGRATION_DIR = os.path.join(CURRENT_DIR, "migration")
CUTTERS_DIR = os.path.join(CURRENT_DIR, "cutters")
TEMP_DIR = os.path.join(CURRENT_DIR, "temp")
SETTINGS_DIR = os.path.join(CURRENT_DIR, "settings")
TEMP_CONFIG_FILE_NAME = "temp_config.json"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
SETTINGS_PATH = os.path.join(SETTINGS_DIR, "settings.json")
TEMP_CONFIG_PATH = os.path.join(TEMP_DIR, TEMP_CONFIG_FILE_NAME)
DEBUG_MODE = False
INDENT_VALUE = "    "


def get_display_preview(json_obj):
    l = Localization()
    profile_db = App.get_running_app().profile_db
    tool_description = profile_db.get_tool_name(json_obj["cutter_type"])
    material_description = profile_db.get_material_name(json_obj["material"])
    x_corrective_offset = 5
    y_corrective_offset = 14
    preview = get_shape_type(json_obj, l)
    preview += l.get_str("Units") + ": " + json_obj["units"] + "\n"
    preview += l.get_str("Canvas shape dims") + ": \n"
    preview += get_shape_dimensions(json_obj, l)
    preview += l.get_str("Material") + ": " + l.get_str(material_description) + "\n"
    preview += (
        l.get_str("Cutter type")
        + ": "
        + get_translated_description(tool_description)
        + "\n"
    )
    preview += (
        l.get_str("Toolpath offset")
        + ": "
        + l.get_str(json_obj["toolpath_offset"])
        + "\n"
    )
    preview += l.get_str("Cutting depths") + ": \n"
    preview += (
        INDENT_VALUE
        + l.get_str("Material thickness")
        + ": "
        + str(json_obj["cutting_depths"]["material_thickness"])
        + "\n"
    )
    preview += (
        INDENT_VALUE
        + l.get_str("Bottom offset")
        + ": "
        + str(json_obj["cutting_depths"]["bottom_offset"])
        + "\n"
    )
    preview += (
        INDENT_VALUE
        + l.get_str("Auto pass depth")
        + ": "
        + str(
            l.get_str("Yes")
            if json_obj["cutting_depths"]["auto_pass"]
            else l.get_str("No")
        )
        + "\n"
    )
    preview += (
        INDENT_VALUE
        + l.get_str("Depth per pass")
        + ": "
        + str(json_obj["cutting_depths"]["depth_per_pass"])
        + "\n"
    )
    preview += (
        INDENT_VALUE
        + l.get_str("Tabs")
        + ": "
        + str(
            l.get_str("Yes") if json_obj["cutting_depths"]["tabs"] else l.get_str("No")
        )
        + "\n"
    )
    preview += (
        l.get_str("Datum position")
        + ": X: "
        + str(round(json_obj["datum_position"]["x"] + x_corrective_offset, 1))
        + " / Y: "
        + str(round(json_obj["datum_position"]["y"] + y_corrective_offset, 1))
        + "\n"
    )
    return preview


def get_translated_description(description):
    l = Localization()
    desc = ""
    for elem in description.split(" "):
        desc += l.get_str(elem) + " "
    return desc.strip()


def get_shape_type(json_obj, l):
    if json_obj["shape_type"] in ["line", "rectangle"]:
        return (
            l.get_str("Shape type")
            + ": "
            + l.get_str(json_obj["rotation"])
            + " "
            + l.get_str(json_obj["shape_type"])
            + "\n"
        )
    else:
        return l.get_str("Shape type") + ": " + l.get_str(json_obj["shape_type"]) + "\n"


def get_shape_dimensions(json_obj, l):
    if json_obj["shape_type"] == "rectangle":
        dims = (
            INDENT_VALUE
            + l.get_str("X")
            + ": "
            + str(json_obj["canvas_shape_dims"]["x"])
            + "\n"
        )
        dims += (
            INDENT_VALUE
            + l.get_str("Y")
            + ": "
            + str(json_obj["canvas_shape_dims"]["y"])
            + "\n"
        )
        dims += (
            INDENT_VALUE
            + l.get_str("R")
            + ": "
            + str(json_obj["canvas_shape_dims"]["r"])
            + "\n"
        )
    elif json_obj["shape_type"] == "square":
        dims = (
            INDENT_VALUE
            + l.get_str("Y")
            + ": "
            + str(json_obj["canvas_shape_dims"]["y"])
            + "\n"
        )
        dims += (
            INDENT_VALUE
            + l.get_str("R")
            + ": "
            + str(json_obj["canvas_shape_dims"]["r"])
            + "\n"
        )
    elif json_obj["shape_type"] == "circle":
        dims = (
            INDENT_VALUE
            + l.get_str("D")
            + ": "
            + str(json_obj["canvas_shape_dims"]["d"])
            + "\n"
        )
    elif json_obj["shape_type"] == "line":
        dims = (
            INDENT_VALUE
            + l.get_str("L")
            + ": "
            + str(json_obj["canvas_shape_dims"]["l"])
            + "\n"
        )
    else:
        dims = ""
    return dims


def migrate_v1_to_v2(config, file_path):
    """
    Migrate a configuration from version 1.0 to 2.0.
    The changes include:
        - Changing the cutter_type from the "tool_6mm.json" format to the "0000" format.
        - Adding a 'material' field with the Plasterboard uid as the default value.
    """
    tool_migration = os.path.join(MIGRATION_DIR, "tool_migration_0_1.json")
    with open(tool_migration) as f:
        tool_migration = json.load(f)
    for field_name in config:
        if field_name == "cutter_type" and config[field_name] in tool_migration:
            config[field_name] = tool_migration[config[field_name]]["uid"]
            break
    config["material"] = "0010"
    config["version"] = "2.0"
    config["cutting_depths"]["tabs"] = False
    Logger.info(
        f"Migrated configuration '{os.path.basename(file_path)}' to version 2.0"
    )
    return config


class DWTConfig(EventDispatcher):
    active_config_name = StringProperty("")
    active_config = ObjectProperty(config_classes.Configuration.default())
    active_cutter = ObjectProperty(config_classes.Cutter.default())
    active_profile = ObjectProperty(config_classes.Profile.default())
    show_z_height_reminder = True

    def __init__(self, screen_drywall_cutter=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen_drywall_cutter = screen_drywall_cutter
        self.profile_db = App.get_running_app().profile_db
        if ModelManagerSingleton().is_machine_drywall():
            self.app_type = config_options.AppType.DRYWALL_CUTTER
        else:
            self.app_type = config_options.AppType.SHAPES
        most_recent_config_path = self.get_most_recent_config()
        if most_recent_config_path:
            self.load_config(most_recent_config_path)
        else:
            self.load_temp_config()

    @staticmethod
    def get_most_recent_config():
        """
        Get most recent config from settings.json

        :return: the most recently used config path
        """
        if not os.path.exists(SETTINGS_PATH):
            Logger.warning("No settings file found")
            return None
        Logger.debug("Reading most recent config")
        with open(SETTINGS_PATH) as settings_f:
            j_obj = json.load(settings_f)
            return j_obj["most_recent_config"]

    @staticmethod
    def set_most_recent_config(config_path):
        """
        Set the most recent config in settings.json

        :param config_path: the name of the most recently used config
        :return:
        """
        Logger.debug("Writing most recent config: " + config_path.split(os.sep)[-1])
        with open(SETTINGS_PATH, "w+") as settings_f:
            j_obj = {"most_recent_config": config_path}
            json.dump(j_obj, settings_f)

    @staticmethod
    def is_valid_configuration(config_name):
        """
        Checks if a configuration file is valid/complete.

        :param config_name: The name of the configuration file to check.
        :return: True if the configuration file is valid/complete, otherwise False.
        """
        # TODO: Fix for Python 3.12
        # file_path = os.path.join(CONFIGURATIONS_DIR, config_name)
        # if not os.path.exists(file_path):
        #     return False
        # with open(file_path) as f:
        #     cfg = json.load(f)
        # valid_field_names = inspect.getargspec(
        #     config_classes.Configuration.__init__
        # ).args[1:]
        # for field_name in valid_field_names:
        #     if field_name not in cfg:
        #         return False
        # field_count = len(cfg)
        # valid_field_count = len(
        #     inspect.getargspec(config_classes.Configuration.__init__).args[1:]
        # )
        # if field_count < valid_field_count:
        #     return False
        # if cfg["cutter_type"].endswith(".json"):
        #     return False
        return True

    @staticmethod
    def fix_config(config_name):
        """
        Fixes a configuration file by adding any missing fields.

        :param config_name: The name of the configuration file to fix.
        :return: True if the configuration file was fixed, otherwise False.
        """
        file_path = os.path.join(CONFIGURATIONS_DIR, config_name)
        if not os.path.exists(file_path):
            return False
        with open(file_path) as f:
            cfg = json.load(f)
        valid_field_names = inspect.getargspec(
            config_classes.Configuration.__init__
        ).args[1:]
        config_version = cfg.get("version", "1.0")
        if config_version == "1.0":
            cfg = migrate_v1_to_v2(cfg, file_path)
        for field_name in valid_field_names:
            if field_name not in cfg:
                cfg[field_name] = getattr(
                    config_classes.Configuration.default(), field_name
                )
        with open(file_path, "w") as f:
            json.dump(cfg, f, indent=4, default=lambda o: o.__dict__)
        Logger.debug("Fixed configuration: " + config_name)
        return True

    def load_config(self, config_path):
        """
        Loads a configuration file from the configuration directory.

        :param config_path: The path of the configuration file to load.
        """
        if not os.path.exists(config_path):
            Logger.error("Configuration file doesn't exist: " + config_path)
            self.load_temp_config()
            return
        if not self.is_valid_configuration(config_path):
            if not self.fix_config(config_path):
                self.active_config = config_classes.Configuration.default()
                self.save_temp_config()
        Logger.debug("Loading configuration: " + config_path)
        with open(config_path) as f:
            self.active_config = config_classes.Configuration.from_json(
                json_data=json.load(f)
            )
        config_name = config_path.split(os.sep)[-1]
        self.active_config_name = config_name
        if config_path != TEMP_CONFIG_PATH:
            self.set_most_recent_config(config_path)
        self.load_cutter(self.active_config.cutter_type)
        self.load_new_profile()

    def load_new_profile(self):
        """
        Loads a new profile based on the active configuration.
        """
        if (
            self.active_config.material != "-0001"
            and self.active_config.cutter_type != "-0001"
        ):
            generic_tool_id = self.profile_db.get_tool_generic_id(
                self.active_config.cutter_type
            )
            profile_id = self.profile_db.get_profile_id(
                self.active_config.material, generic_tool_id
            )
            if profile_id:
                Logger.info("Loading new profile: " + profile_id)
                self.active_profile = config_classes.Profile.from_json(
                    self.profile_db.get_profile(profile_id)
                )
            else:
                Logger.error(
                    f"Unable to load profile with material {self.active_config.material} and generic tool ID {generic_tool_id}"
                )

    def save_config(self, config_path):
        """
        Saves the active configuration to the configuration directory.

        :param config_path: The path to save the config to
        """
        Logger.debug("Saving configuration: " + config_path)
        self.cleanup_active_config()
        with open(config_path, "w") as f:
            json.dump(self.active_config, f, indent=4, default=lambda o: o.__dict__)
        if config_path != TEMP_CONFIG_PATH:
            self.active_config_name = config_path.split(os.sep)[-1]
            self.set_most_recent_config(config_path)

    def cleanup_active_config(self):
        if self.active_config.shape_type == "rectangle":
            self.active_config.canvas_shape_dims.d = 0
            self.active_config.canvas_shape_dims.l = 0
        elif self.active_config.shape_type == "square":
            self.active_config.canvas_shape_dims.x = 0
            self.active_config.canvas_shape_dims.d = 0
            self.active_config.canvas_shape_dims.l = 0
        elif self.active_config.shape_type == "circle":
            self.active_config.canvas_shape_dims.x = 0
            self.active_config.canvas_shape_dims.y = 0
            self.active_config.canvas_shape_dims.r = 0
            self.active_config.canvas_shape_dims.l = 0
        elif self.active_config.shape_type == "line":
            self.active_config.canvas_shape_dims.x = 0
            self.active_config.canvas_shape_dims.y = 0
            self.active_config.canvas_shape_dims.r = 0
            self.active_config.canvas_shape_dims.d = 0

    def load_cutter(self, cutter_uid):
        """
        Loads a cutter from the database.

        :param cutter_uid: The uid of the cutter to load.
        """
        cutter = self.profile_db.get_tool(cutter_uid)
        if not cutter:
            Logger.error("Cutter doesn't exist: " + cutter_uid)
            Logger.info("Loading default cutter...")
            self.active_cutter = config_classes.Cutter.default()
            self.active_config.cutter_type = self.active_cutter.uid
            return
        Logger.debug("Loading cutter: " + cutter_uid)
        self.active_cutter = config_classes.Cutter.from_json(cutter)
        self.active_config.cutter_type = self.active_cutter.uid

    @staticmethod
    def get_available_cutter_names():
        """
        TODO: Refactor, it doesn't need the names anymore
        :return: A list of the available cutter names and their file names.
        """
        cutters = {}
        for cutter_file in sorted(os.listdir(CUTTERS_DIR)):
            file_path = os.path.join(CUTTERS_DIR, cutter_file)
            if not os.path.isfile(file_path):
                continue
            with open(file_path) as f:
                cutter = config_classes.Cutter.from_json(json.load(f))
                cutters[cutter.description] = {
                    "cutter_path": cutter_file,
                    "image_path": cutter.image,
                    "type": cutter.type,
                    "size": cutter.dimensions.diameter
                    if cutter.dimensions.diameter
                    else cutter.dimensions.angle,
                }
        return cutters

    def get_available_cutters(self):
        """
        Returns a list of the available cutters for the current configuration.
        :return: A list of the available cutters.
        """
        cutters = {}
        for cutter_file in sorted(os.listdir(CUTTERS_DIR)):
            file_path = os.path.join(CUTTERS_DIR, cutter_file)
            if not os.path.isfile(file_path):
                continue
            with open(file_path) as f:
                cutter = config_classes.Cutter.from_json(json.load(f))
            if self.app_type.value not in cutter.apps:
                continue
            cutters[cutter.description] = {
                "cutter_path": cutter_file,
                "image_path": cutter.image,
                "type": cutter.type,
                "size": cutter.dimensions.diameter
                if cutter.dimensions.diameter
                else cutter.dimensions.angle,
            }
        return cutters

    def save_temp_config(self):
        """
        Saves the active configuration to a temporary file.

        This is used to save the configuration when the Drywall Cutter screen is left.
        """
        self.save_config(TEMP_CONFIG_PATH)

    def load_temp_config(self):
        """
        Loads the temporary configuration file.

        This is used to load the configuration when the Drywall Cutter screen is loaded.
        """
        if not os.path.exists(TEMP_CONFIG_PATH):
            Logger.warning(
                "Temporary configuration file doesn't exist! Creating a new one."
            )
            self.active_config = config_classes.Configuration.default()
            self.save_temp_config()
            return
        self.load_config(TEMP_CONFIG_PATH)

    def on_parameter_change(self, parameter_name, parameter_value):
        """
        Should be called when a parameter is changed in the UI.
        Bind this to the widget, e.g.: on_value: root.on_parameter_change('parameter_name', self.value)
        If the parameter is nested, use a dot to separate the names, e.g.: 'nested_parameter_name.parameter_name'

        :param parameter_name: The name of the parameter that was changed.
        :param parameter_value: The new value of the parameter.
        """
        Logger.debug(
            "Parameter changed: " + parameter_name + " = " + str(parameter_value)
        )
        if (
            parameter_name == "material"
            and parameter_value != self.active_config.material
        ):
            self.show_z_height_reminder = True
        if (
            "." in parameter_name
            and parameter_name.split(".")[-1] == "material_thickness"
            and parameter_value != self.active_config.cutting_depths.material_thickness
        ):
            self.show_z_height_reminder = True
        if (
            parameter_name == "cutter_type"
            and parameter_value != self.active_config.cutter_type
        ):
            self.load_cutter(parameter_value)
            self.load_new_profile()
            self.show_z_height_reminder = True
        if "." in parameter_name:
            parameter_names = parameter_name.split(".")
            parameter = self.active_config
            for parameter_name in parameter_names[:-1]:
                parameter = getattr(parameter, parameter_name)
            if getattr(parameter, parameter_names[-1]) != parameter_value:
                self.active_config_name = "New Configuration"
            setattr(parameter, parameter_names[-1], parameter_value)
        else:
            if getattr(self.active_config, parameter_name) != parameter_value:
                self.active_config_name = "New Configuration"
            setattr(self.active_config, parameter_name, parameter_value)
        if not (
            self.active_config.shape_type == "geberit"
            and self.active_cutter.dimensions.tool_diameter is None
        ):
            self.screen_drywall_cutter.drywall_shape_display_widget.check_datum_and_extents()
