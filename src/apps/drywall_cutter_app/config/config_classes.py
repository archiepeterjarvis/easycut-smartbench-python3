"""This module contains the classes used to store the configuration data for the drywall cutter app."""

import json
import os
from core.job.database.profile_database import ProfileDatabase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS_DIR = os.path.join(CURRENT_DIR, "settings")
DEFAULT_CONFIG_PATH = os.path.join(SETTINGS_DIR, "default_config.json")
DEFAULT_CUTTER_UID = "-0001"


class Cutter:
    """Class to store the cutter data."""

    def __init__(
        self,
        uid,
        description,
        manufacturer,
        manufacturer_part_number,
        tool_type,
        generic_definition,
        dimensions,
        flutes,
        available_isas,
        **kwargs,
    ):
        self.uid = uid
        self.description = description.encode("utf-8")
        self.manufacturer = str(manufacturer)
        self.manufacturer_part_number = str(manufacturer_part_number)
        self.tool_type = str(tool_type)
        self.generic_definition = ToolGenericDefinition(**generic_definition)
        self.dimensions = Dimensions(**dimensions)
        self.flutes = Flutes(**flutes)
        self.available_isas = available_isas

    @classmethod
    def from_json(cls, json_data):
        """Create a Cutter object from a JSON object."""
        return Cutter(**json_data)

    @classmethod
    def default(cls):
        """Get the default cutter."""
        profile_db = ProfileDatabase()
        default_cutter = profile_db.get_tool(DEFAULT_CUTTER_UID)
        return Cutter.from_json(default_cutter)


class ToolGenericDefinition:
    """Class to store the cutter generic definition."""

    def __init__(
        self,
        uid,
        string,
        dimension,
        unit,
        type,
        toolpath_offsets,
        required_operations,
        **kwargs,
    ):
        self.uid = uid
        self.string = str(string)
        self.dimension = int(dimension)
        self.unit = str(unit)
        self.type = str(type)
        self.toolpath_offsets = AllowableToolpathOffsets(**toolpath_offsets)
        self.required_operations = RequiredOperations(**required_operations)


class RequiredOperations:
    """Class to store the required operations."""

    def __init__(self, lead_in, **kwargs):
        self.lead_in = bool(lead_in)


class Dimensions:
    """Class to store the cutter dimensions."""

    def __init__(self, shank_diameter, tool_diameter, unit, angle, **kwargs):
        self.shank_diameter = float(shank_diameter)
        self.tool_diameter = float(tool_diameter) if tool_diameter else None
        self.unit = str(unit)
        self.angle = int(angle) if angle else None


class AllowableToolpathOffsets:
    """Class to store the allowable toolpath offsets."""

    def __init__(self, inside, outside, on, pocket, **kwargs):
        self.inside = inside
        self.outside = outside
        self.on = on
        self.pocket = pocket


class Flutes:
    """Class to store the cutter flutes."""

    def __init__(self, type, lengths, quantity, material, coated, coating, **kwargs):
        self.type = str(type)
        self.lengths = FluteLengths(**lengths)
        self.quantity = int(quantity)
        self.material = str(material)
        self.coated = bool(coated)
        self.coating = str(coating) if coating else None


class FluteLengths:
    """Class to store the cutter flute lengths."""

    def __init__(self, upcut_straight, downcut, total, unit, **kwargs):
        self.upcut_straight = int(upcut_straight)
        self.downcut = int(downcut)
        self.total = int(total)
        self.unit = str(unit)


class CanvasShapeDims:
    """Class to store the canvas shape dimensions."""

    def __init__(self, x, y, r, d, l, **kwargs):
        self.x = x
        self.y = y
        self.r = r
        self.d = d
        self.l = l


class CuttingDepths:
    """Class to store the cutting depths."""

    def __init__(
        self, material_thickness, bottom_offset, auto_pass, depth_per_pass, tabs=False
    ):
        self.material_thickness = material_thickness
        self.bottom_offset = bottom_offset
        self.auto_pass = auto_pass
        self.depth_per_pass = depth_per_pass
        self.tabs = tabs


class DatumPosition:
    """Class to store the datum position."""

    def __init__(self, x, y, **kwargs):
        self.x = x
        self.y = y


class Profile:
    """Class to store the profile data"""

    def __init__(
        self,
        uid,
        generic_tool,
        material,
        cutting_parameters,
        applicable_tools,
        **kwargs,
    ):
        self.uid = str(uid)
        self.generic_tool = ProfileGenericTool(**generic_tool)
        self.material = ProfileMaterial(**material)
        self.cutting_parameters = ProfileCuttingParameters(**cutting_parameters)
        self.applicable_tools = applicable_tools

    @classmethod
    def from_json(cls, json_data):
        """Create a Configuration object from a JSON object."""
        return Profile(**json_data)

    @classmethod
    def default(cls):
        """Get the default configuration."""
        profile_db = ProfileDatabase()
        default_profile = profile_db.get_profile("-0001")
        return Profile.from_json(default_profile)


class ProfileGenericTool:
    """Class to store the profile generic tool data"""

    def __init__(self, uid, description, **kwargs):
        self.uid = str(uid)
        self.description = str(description)


class ProfileMaterial:
    """Class to store the profile material data"""

    def __init__(self, uid, description, **kwargs):
        self.uid = str(uid)
        self.description = str(description)


class ProfileCuttingParameters:
    """Class to store the profile cutting parameters data"""

    def __init__(
        self,
        recommendations,
        spindle_speed,
        max_feedrate,
        plungerate,
        target_tool_load,
        **kwargs,
    ):
        self.recommendations = ProfileRecommendations(**recommendations)
        self.spindle_speed = int(spindle_speed)
        self.max_feedrate = int(max_feedrate)
        self.plungerate = int(plungerate)
        self.target_tool_load = int(target_tool_load)


class ProfileRecommendations:
    """Class to store the profile recommendations data"""

    def __init__(self, stepdown, stepover, unit, cutting_direction, **kwargs):
        self.stepdown = float(stepdown)
        self.stepover = float(stepover) if stepover else None
        self.unit = str(unit)
        self.cutting_direction = str(cutting_direction)


class Configuration:
    """Class to store the configuration data."""

    def __init__(
        self,
        shape_type,
        units,
        rotation,
        canvas_shape_dims,
        material,
        cutter_type,
        toolpath_offset,
        cutting_depths,
        datum_position,
        **kwargs,
    ):
        try:
            self.version = str(kwargs["version"])
        except KeyError:
            self.version = "1.0"
        self.shape_type = str(shape_type)
        self.units = str(units)
        self.rotation = str(rotation)
        self.canvas_shape_dims = CanvasShapeDims(**canvas_shape_dims)
        self.material = str(material)
        self.cutter_type = str(cutter_type)
        self.toolpath_offset = str(toolpath_offset)
        self.cutting_depths = CuttingDepths(**cutting_depths)
        self.datum_position = DatumPosition(**datum_position)

    @classmethod
    def from_json(cls, json_data):
        """Create a Configuration object from a JSON object."""
        return Configuration(**json_data)

    @classmethod
    def default(cls):
        """Get the default configuration."""
        with open(DEFAULT_CONFIG_PATH) as f:
            return Configuration.from_json(json.load(f))


if __name__ == "__main__":
    print(Cutter.default().description)
