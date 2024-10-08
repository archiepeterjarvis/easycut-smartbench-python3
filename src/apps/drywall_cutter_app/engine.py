"""
Author: BP
Description: This module contains the GCodeEngine class, which is responsible for producing gcode instructions for cutting shapes. The class contains methods for producing gcode instructions for cutting rectangles, circles, and custom shapes. The class also contains methods for reading in gcode files, adjusting feeds and speeds, and replacing Z values. The class is used by the DrywallCutterApp class to produce gcode instructions for cutting shapes.

Working theory:

read in data
for simple shapes:
    is it clockwise?
        correct direction
    find shape centre
    apply inside/outside offset
    are there corner rads?
        offset corner radius
        add corner coordinates
calculate pass depths
produce gcode
tidy gcode
write to output file
"""

import decimal
import os
import re
from core import paths
from apps.drywall_cutter_app.config.config_options import (
    CuttingDirectionOptions,
    ShapeOptions,
)
from apps.drywall_cutter_app.engine_utils.tabutilities import TabUtilities
from core.logging.logging_system import Logger


class GCodeEngine:
    def __init__(self, router_machine, dwt_config, coordinate_system):
        self.config = dwt_config
        self.m = router_machine
        self.cs = coordinate_system
        self.tab_utils = TabUtilities(self.config)
        self.cutter_diameter = 0
        self.finishing_passes = 1
        self.finishing_stepover = 0.5
        self.finishing_stepdown = 12
        self.x = 0
        self.y = 1
        self.custom_gcode_shapes = ["geberit"]
        self.source_folder_path = os.path.join(paths.DWT_APP_PATH, "gcode")
        self.CORNER_RADIUS_THRESHOLD = 0.09

    def rectangle_coordinates(self, x, y, x_min=0, y_min=0):
        if (
            x <= 0
            or y <= 0
            and self.config.active_config.shape_type.lower()
            not in ["circle", "geberit", "line"]
        ):
            return None
        top_left = x_min, y
        top_right = x, y
        bottom_left = x_min, y_min
        bottom_right = x, y_min
        return [bottom_left, top_left, top_right, bottom_right]

    def find_centre(self, coordinates, x_offset=0, y_offset=0):
        x_sum = 0
        y_sum = 0
        coordinates = list(set(coordinates))
        for x, y in coordinates:
            x_sum += x + x_offset
            y_sum += y + y_offset
        centre_x = x_sum / len(coordinates)
        centre_y = y_sum / len(coordinates)
        return centre_x, centre_y

    def find_corner_rads(self, radius):
        return radius > self.CORNER_RADIUS_THRESHOLD

    def is_clockwise(self, coordinates):
        total = 0
        for i in xrange(len(coordinates)):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[(i + 1) % len(coordinates)]
            total += (x2 - x1) * (y2 + y1)
        return total > 0

    def correct_orientation(self, coordinates, clockwise):
        if not clockwise:
            return coordinates[::-1]
        return coordinates

    def add_corner_coordinates(self, coordinates, shape_centre, corner_radius):
        new_coordinates = []
        for coordinate in coordinates:
            if (
                coordinate[self.x] < shape_centre[self.x]
                and coordinate[self.y] < shape_centre[self.y]
            ):
                rad_point_1 = coordinate[self.x], coordinate[self.y] + corner_radius
                rad_point_2 = coordinate[self.x] + corner_radius, coordinate[self.y]
            elif (
                coordinate[self.x] < shape_centre[self.x]
                and coordinate[self.y] > shape_centre[self.y]
            ):
                rad_point_1 = coordinate[self.x] + corner_radius, coordinate[self.y]
                rad_point_2 = coordinate[self.x], coordinate[self.y] - corner_radius
            elif (
                coordinate[self.x] > shape_centre[self.x]
                and coordinate[self.y] > shape_centre[self.y]
            ):
                rad_point_1 = coordinate[self.x], coordinate[self.y] - corner_radius
                rad_point_2 = coordinate[self.x] - corner_radius, coordinate[self.y]
            elif (
                coordinate[self.x] > shape_centre[self.x]
                and coordinate[self.y] < shape_centre[self.y]
            ):
                rad_point_1 = coordinate[self.x] - corner_radius, coordinate[self.y]
                rad_point_2 = coordinate[self.x], coordinate[self.y] + corner_radius
            new_coordinates.append(rad_point_1)
            new_coordinates.append(rad_point_2)
        return new_coordinates

    def calculate_corner_radius_offset(self, offset_type, tool_diamter):
        tool_radius = tool_diamter / 2
        if offset_type == "inside":
            offset_for_rads = -1 * tool_radius
        elif offset_type == "outside":
            offset_for_rads = tool_radius
        else:
            offset_for_rads = 0
        return offset_for_rads

    def apply_offset(self, coordinates, offset_type, tool_diameter, shape_centre):
        x_offset = 0
        y_offset = 0
        adjusted_coordinates = []
        if offset_type != None:
            tool_radius = tool_diameter / 2
            for coordinate in coordinates:
                if offset_type == "inside":
                    if coordinate[self.x] > shape_centre[self.x]:
                        x_offset = -1 * tool_radius
                    else:
                        x_offset = tool_radius
                    if coordinate[self.y] > shape_centre[self.y]:
                        y_offset = -1 * tool_radius
                    else:
                        y_offset = tool_radius
                elif offset_type == "outside":
                    if coordinate[self.x] < shape_centre[self.x]:
                        x_offset = -1 * tool_radius
                    else:
                        x_offset = tool_radius
                    if coordinate[self.y] < shape_centre[self.y]:
                        y_offset = -1 * tool_radius
                    else:
                        y_offset = tool_radius
                new_coordinate = (
                    coordinate[self.x] + x_offset,
                    coordinate[self.y] + y_offset,
                )
                adjusted_coordinates.append(new_coordinate)
        else:
            adjusted_coordinates = coordinates
        return adjusted_coordinates

    def calculate_pass_depths(self, total_cut_depth, pass_depth):
        if total_cut_depth <= 0 or pass_depth <= 0:
            raise ValueError("Total cut depth and pass depth must be positive values.")
        pass_depths = []
        current_depth = pass_depth
        while current_depth < total_cut_depth:
            pass_depths.append(current_depth)
            current_depth += pass_depth
        try:
            if max(pass_depths) < total_cut_depth:
                pass_depths.append(total_cut_depth)
        except:
            pass_depths = [total_cut_depth]
        return pass_depths

    def determine_cut_direction_clockwise(self, offset_type, climb):
        if offset_type in ["inside", "on"]:
            return climb
        elif offset_type == "outside":
            return not climb
        else:
            raise ValueError(
                f"Offset type must be 'on, 'inside' or 'outside'. Got '{offset_type}'."
            )

    def swap_lines_after_keyword(self, input_list, keyword):
        i = 0
        while i < len(input_list):
            if keyword.lower() in input_list[i].lower():
                if i + 2 < len(input_list):
                    input_list[i + 1], input_list[i + 2] = (
                        input_list[i + 2],
                        input_list[i + 1],
                    )
                i += 3
            else:
                i += 1
        return input_list

    def replace_mode_after_keyword(self, input_list, keyword, replacement_mode):
        for i in xrange(len(input_list) - 1):
            if keyword.lower() in input_list[i].lower():
                if i + 1 < len(input_list):
                    input_list[i + 1] = replacement_mode + input_list[i + 1][2:]
        return input_list

    def cut_rectangle(
        self,
        coordinates,
        datum_x,
        datum_y,
        offset,
        tool_diameter,
        is_climb,
        corner_radius,
        pass_depth,
        feedrate,
        plungerate,
        total_cut_depth,
        z_safe_distance,
        pass_type,
        simulate,
        first_plunge=True,
    ):
        if offset == "pocket":
            offset = "inside"
        coordinates = self.correct_orientation(
            coordinates, self.is_clockwise(coordinates)
        )
        shape_centre = self.find_centre(coordinates[:-1], 0, 0)
        offset_coordinates = self.apply_offset(
            coordinates, offset, tool_diameter, shape_centre
        )
        radii_present = self.find_corner_rads(corner_radius)
        final_coordinates = offset_coordinates
        if radii_present:
            adjusted_corner_radius = (
                corner_radius
                + self.calculate_corner_radius_offset(offset, tool_diameter)
            )
            if adjusted_corner_radius > 0:
                final_coordinates = self.add_corner_coordinates(
                    reversed(offset_coordinates), shape_centre, adjusted_corner_radius
                )
            else:
                radii_present = False
        pass_depths = self.calculate_pass_depths(total_cut_depth, pass_depth)
        clockwise_cutting = self.determine_cut_direction_clockwise(offset, is_climb)
        tool_lifting = z_safe_distance > 0 or first_plunge
        if clockwise_cutting:
            final_coordinates = final_coordinates[::-1]
        if clockwise_cutting:
            arc_instruction = "G2"
        else:
            arc_instruction = "G3"
        cutting_lines = []
        for depth in pass_depths:
            if not simulate:
                gcode_instruction = "(Offset: {})\n({})\n".format(offset, pass_type)
                cutting_lines.append(gcode_instruction)
                cutting_lines.append("G1 Z-{} F{}\n".format(depth, plungerate))
            else:
                gcode_instruction = "(Simulation pass)\n"
                cutting_lines.append(gcode_instruction)
                cutting_lines.append("G1 Z{} F{}\n".format(depth, plungerate))
            if not radii_present:
                for coordinate in final_coordinates[::-1]:
                    if tool_lifting:
                        add_feedrate_to_line = 1 == final_coordinates.index(coordinate)
                    else:
                        add_feedrate_to_line = 0 == final_coordinates.index(coordinate)
                    if first_plunge:
                        add_feedrate_to_line = 3 == final_coordinates.index(coordinate)
                    gcode_instruction = "G1 X{} Y{} {}\n".format(
                        coordinate[0] + datum_x,
                        coordinate[1] + datum_y,
                        "F%s" % feedrate if add_feedrate_to_line else "",
                    )
                    cutting_lines.append(gcode_instruction)
            else:
                arc_flag = True
                for coordinate in final_coordinates[:-1]:
                    if tool_lifting:
                        add_feedrate_to_line = 1 == final_coordinates.index(coordinate)
                    else:
                        add_feedrate_to_line = 0 == final_coordinates.index(coordinate)
                    if first_plunge:
                        add_feedrate_to_line = 1 == final_coordinates.index(coordinate)
                    if arc_flag:
                        gcode_instruction = "G1 X{} Y{} {}\n".format(
                            round(coordinate[0] + datum_x, 2),
                            round(coordinate[1] + datum_y, 2),
                            "F%s" % feedrate if add_feedrate_to_line else "",
                        )
                    else:
                        gcode_instruction = "{} X{} Y{} R{} {}\n".format(
                            arc_instruction,
                            round(coordinate[0] + datum_x, 2),
                            round(coordinate[1] + datum_y, 2),
                            round(adjusted_corner_radius, 2),
                            "F%s" % feedrate if add_feedrate_to_line else "",
                        )
                    arc_flag = not arc_flag
                    cutting_lines.append(gcode_instruction)
            cutting_lines.append("G1 Z%s F%d\n\n" % (z_safe_distance, plungerate))
        gcode_pass_headers = [
            "New pass",
            "Roughing pass",
            "Finishing pass",
            "Simulation pass",
        ]
        if tool_lifting:
            for header in gcode_pass_headers:
                cutting_lines = self.swap_lines_after_keyword(cutting_lines, header)
                cutting_lines = self.replace_mode_after_keyword(
                    cutting_lines, header, "G0"
                )
        return cutting_lines

    def cut_line(
        self,
        datum_x,
        datum_y,
        length,
        tool_diameter,
        orientation,
        pass_depth,
        feedrate,
        plungerate,
        total_cut_depth,
        z_safe_distance,
        simulate=False,
    ):
        pass_depths = self.calculate_pass_depths(total_cut_depth, pass_depth)
        tool_radius = tool_diameter / 2
        x = 0
        y = 1
        direction_flag = True
        gcode_lines = [f"G0 Z{z_safe_distance}"]
        if orientation == "vertical":
            start_coordinate = [datum_x + tool_radius, datum_y]
            end_coordinate = [datum_x + length - tool_radius, datum_y]
        elif orientation == "horizontal":
            start_coordinate = [datum_x, datum_y + tool_radius]
            end_coordinate = [datum_x, datum_y + length - tool_radius]
        else:
            raise ValueError(
                f"Orientation must be 'vertical' or 'horizontal'. Got '{orientation}'"
            )
        gcode_lines.append(f"G0 X{start_coordinate[x]} Y{start_coordinate[y]}")
        for depth in pass_depths:
            if simulate:
                gcode_lines.append(f"G1 Z{depth} F{plungerate}")
            else:
                gcode_lines.append(f"G1 Z-{depth} F{plungerate}")
            if not direction_flag:
                gcode_lines.append(
                    f"G1 X{start_coordinate[x]} Y{start_coordinate[y]} F{feedrate}"
                )
            else:
                gcode_lines.append(
                    f"G1 X{end_coordinate[x]} Y{end_coordinate[y]} F{feedrate}"
                )
            direction_flag = not direction_flag
        gcode_lines.append(f"G1 Z{z_safe_distance} F{plungerate}")
        for i in range(len(gcode_lines)):
            gcode_lines[i] = gcode_lines[i] + "\n"
        return gcode_lines

    def find_and_read_gcode_file(
        self, directory, shape_type, tool_diameter, orientation=None
    ):
        for file in os.listdir(directory):
            filename = file.lower().strip()
            if (
                shape_type in filename
                and str(tool_diameter)[:-2] + "mm" in filename
                and (orientation is None or orientation in filename)
            ):
                file_path = os.path.join(directory, file)
                if os.path.exists(file_path):
                    try:
                        with open(file_path) as file:
                            Logger.debug(
                                f"Reading {shape_type} gcode file: {file_path}"
                            )
                            return file.readlines()
                    except OSError:
                        Logger.Warning("An error occurred while reading the Gcode file")
        raise OSError("Gcode file not found")

    def adjust_feeds_and_speeds(self, gcode_lines, feedrate, plungerate, spindle_speed):
        adjusted_lines = []
        feedrate_pattern = re.compile("G1.*?[XY].*?F([\\d.]+)", re.IGNORECASE)
        plungerate_pattern = re.compile("G1.*?[Z].*?F([\\d.]+)", re.IGNORECASE)
        spindle_speed_pattern = re.compile("S\\d.+", re.IGNORECASE)
        for line in gcode_lines:
            line = line.upper()
            if "F" in line and feedrate_pattern.search(line) and "Z" not in line:
                match = feedrate_pattern.search(line)
                line = line.replace(match.group(1), str(feedrate))
            elif (
                "Z" in line
                and plungerate_pattern.search(line)
                and ("X" not in line and "Y" not in line)
            ):
                match = plungerate_pattern.search(line)
                line = line.replace(match.group(1), str(plungerate))
            line = spindle_speed_pattern.sub("S" + str(spindle_speed), line)
            adjusted_lines.append(line)
        return adjusted_lines

    def extract_cut_depth_and_z_safe_distance(self, gcode_lines):
        cut_depth_pattern = "Cut depth: (-?\\d+\\.\\d+)"
        z_safe_distance_pattern = "Z safe distance: (\\d+\\.\\d+)"
        cut_depth_value = None
        z_safe_distance_value = None
        if not gcode_lines:
            raise Exception("Gcode file is empty.")
        for string in gcode_lines:
            if cut_depth_value is None:
                cut_depth_match = re.search(cut_depth_pattern, string, re.IGNORECASE)
                if cut_depth_match:
                    cut_depth_value = cut_depth_match.group(1)
            if z_safe_distance_value is None:
                z_safe_distance_match = re.search(
                    z_safe_distance_pattern, string, re.IGNORECASE
                )
                if z_safe_distance_match:
                    z_safe_distance_value = z_safe_distance_match.group(1)
            if cut_depth_value and z_safe_distance_value:
                break
        if cut_depth_value is None or z_safe_distance_value is None:
            raise Exception("Unable to gather cut depth and Z safe distance data.")
        return cut_depth_value, z_safe_distance_value

    def replace_cut_depth_and_z_safe_distance(
        self,
        gcode_lines,
        gcode_cut_depth,
        gcode_z_safe_distance,
        new_cut_depth,
        new_z_safe_distance,
    ):
        output = []
        for line in gcode_lines:
            if "z" + str(gcode_cut_depth) in line.strip().lower():
                line = re.sub("Z[-+]?\\d*\\.?\\d+", f"Z{new_cut_depth}", line)
            elif "z" + str(gcode_z_safe_distance) in line.strip().lower():
                line = re.sub("Z[-+]?\\d*\\.?\\d+", f"Z{new_z_safe_distance}", line)
            output.append(line)
        return output

    def apply_datum_offset(self, gcode_lines, x_adjustment, y_adjustment):
        if x_adjustment == 0 and y_adjustment == 0:
            return gcode_lines
        adjusted_lines = []
        for line in gcode_lines:
            if line.startswith("G1Z") or line.startswith("G1 Z"):
                adjusted_lines.append(line)
                continue
            parts = re.findall("[A-Z][0-9.-]+", line)
            adjusted_parts = ""
            for part in parts:
                if part.startswith("X"):
                    x_value = float(part[1:])
                    adjusted_x = x_value + x_adjustment
                    adjusted_parts += f" X{self.format_float(adjusted_x)}"
                elif part.startswith("Y"):
                    y_value = float(part[1:])
                    adjusted_y = y_value + y_adjustment
                    adjusted_parts += f" Y{self.format_float(adjusted_y)}"
                else:
                    adjusted_parts += part
            adjusted_lines.append(adjusted_parts)
        return adjusted_lines

    def format_float(*args):
        value = args[1]
        if value == int(value):
            return str(int(value))
        else:
            return str(decimal.Decimal(str(value)).normalize())

    def repeat_for_depths(self, gcode_lines, pass_depths, start_line_key, end_line_key):
        output = []
        for depth in pass_depths:
            cut_lines = []
            for line in gcode_lines[start_line_key:end_line_key]:
                cut_line = line.replace("[cut depth]", "-" + str(depth))
                cut_lines.append(cut_line)
            output.extend(cut_lines)
        if end_line_key < len(gcode_lines):
            output.extend(gcode_lines[end_line_key:])
        return output

    def add_partoff(
        self,
        gcode_lines,
        insertion_key,
        start_coordinate,
        end_coordinate,
        pass_depths,
        feedrate,
        plungerate,
        z_safe_distance,
    ):
        x = 0
        y = 1
        insert_index = None
        partoff_gcode = ["(Partoff)"]
        direction_flag = True
        insertion_key = insertion_key.lower()
        for i in range(len(gcode_lines)):
            if insertion_key in gcode_lines[i].lower():
                insert_index = i
                break
        if insert_index is None:
            raise Exception("Unable to find " + insertion_key + " in gcode")
        partoff_gcode.append("G1 Z" + str(z_safe_distance))
        partoff_gcode.append(
            "G0 X"
            + str(start_coordinate[x])
            + " Y"
            + str(start_coordinate[y])
            + "F"
            + str(feedrate)
        )
        for depth in pass_depths:
            if direction_flag:
                partoff_gcode.append("G1 Z-" + str(depth) + " F" + str(plungerate))
                partoff_gcode.append(
                    "G1 X"
                    + str(end_coordinate[x])
                    + " Y"
                    + str(end_coordinate[y])
                    + "F"
                    + str(feedrate)
                )
            else:
                partoff_gcode.append("G1 Z-" + str(depth) + " F" + str(plungerate))
                partoff_gcode.append(
                    "G1 X"
                    + str(start_coordinate[x])
                    + " Y"
                    + str(start_coordinate[y])
                    + "F"
                    + str(feedrate)
                )
            direction_flag = not direction_flag
        partoff_gcode.append("G1 Z" + str(z_safe_distance))
        gcode_part_1 = gcode_lines[:insert_index]
        gcode_part_2 = gcode_lines[insert_index:]
        return gcode_part_1 + partoff_gcode + gcode_part_2

    def read_in_custom_shape_dimensions(self, gcode_lines):
        x_dim_pattern = "Final part x dim: (-?\\d+\\.?\\d*)"
        y_dim_pattern = "Final part y dim: (-?\\d+\\.?\\d*)"
        x_min_pattern = "x min: (-?\\d+\\.?\\d*)"
        y_min_pattern = "y min: (-?\\d+\\.?\\d*)"
        x_dim = None
        y_dim = None
        x_min = None
        y_min = None
        for string in gcode_lines:
            if x_dim is None:
                x_dim_match = re.search(x_dim_pattern, string, re.IGNORECASE)
                if x_dim_match:
                    x_dim = x_dim_match.group(1)
            if y_dim is None:
                y_dim_match = re.search(y_dim_pattern, string, re.IGNORECASE)
                if y_dim_match:
                    y_dim = y_dim_match.group(1)
            if x_min is None:
                x_min_match = re.search(x_min_pattern, string, re.IGNORECASE)
                if x_min_match:
                    x_min = x_min_match.group(1)
            if y_min is None:
                y_min_match = re.search(y_min_pattern, string, re.IGNORECASE)
                if y_min_match:
                    y_min = y_min_match.group(1)
            if x_dim and y_dim and x_min and y_min:
                break
        missing_values = [
            dim
            for dim, value in zip(
                ["x_dim", "y_dim", "x_min", "y_min"], [x_dim, y_dim, x_min, y_min]
            )
            if value is None
        ]
        if missing_values:
            raise Exception(
                "Unable to gather shape dimension data. Missing values: {}".format(
                    ", ".join(missing_values)
                )
            )
        return x_dim, y_dim, x_min, y_min

    def get_custom_shape_extents(self):
        if self.config.active_config.shape_type.lower() in self.custom_gcode_shapes:
            gcode_lines = self.find_and_read_gcode_file(
                self.source_folder_path,
                self.config.active_config.shape_type,
                self.cutter_diameter,
                orientation=self.config.active_config.rotation,
            )
            x_dim_str, y_dim_str, x_min_str, y_min_str = (
                self.read_in_custom_shape_dimensions(gcode_lines)
            )
            x_dim = float(x_dim_str)
            y_dim = float(y_dim_str)
            x_min = float(x_min_str)
            y_min = float(y_min_str)
            return x_dim, y_dim, x_min, y_min
        else:
            raise Exception(
                f"Shape type: {self.config.active_config.shape_type} is not defined as a custom shape."
            )

    def remove_redudant_lines(self, gcode_lines):
        """
        Remove moves that result in no machine movement
        """
        x_pos = 0
        y_pos = 0
        z_pos = 0
        last_x = 0
        last_y = 0
        last_z = 0
        output = []
        for line in gcode_lines:
            if (
                line.startswith("G0")
                or line.startswith("G1")
                or line.startswith("G2")
                or line.startswith("G3")
            ):
                parts = line.split()
                for part in parts:
                    if part.startswith("X"):
                        x_pos = float(part[1:])
                    elif part.startswith("Y"):
                        y_pos = float(part[1:])
                    elif part.startswith("Z"):
                        z_pos = float(part[1:])
                if x_pos != last_x or y_pos != last_y or z_pos != last_z:
                    output.append(line)
                    last_x = x_pos
                    last_y = y_pos
                    last_z = z_pos
            else:
                output.append(line)
        output.append("\n")
        return output

    def engine_run(self, simulate=False):
        filename = self.config.active_config.shape_type + ".nc"
        output_path = os.path.join(paths.DWT_TEMP_GCODE_PATH, filename)
        safe_start_position = "X0 Y0 Z10"
        z_safe_distance = 5
        stepover_z_hop_distance = 0
        cutting_pass_depth = (
            self.config.active_profile.cutting_parameters.recommendations.stepdown
            if self.config.active_config.cutting_depths.auto_pass
            else self.config.active_config.cutting_depths.depth_per_pass
        )
        cutting_lines = []
        simulation_z_height = 5
        simulation_plunge_rate = 750
        simulation_feedrate = 6000
        geberit_partoff = False
        base_tab_spacing = 1
        tab_width = 10
        tab_height = self.config.active_config.cutting_depths.material_thickness * 0.6
        if tab_height > 5:
            tab_height = 5
        three_d_tabs = True
        tab_width = tab_width + self.cutter_diameter
        is_climb = (
            self.config.active_profile.cutting_parameters.recommendations.cutting_direction
            == CuttingDirectionOptions.CLIMB.value
            or self.config.active_profile.cutting_parameters.recommendations.cutting_direction
            == CuttingDirectionOptions.BOTH.value
        )
        if self.config.active_cutter.dimensions.tool_diameter is not None:
            self.cutter_diameter = self.config.active_cutter.dimensions.tool_diameter
        else:
            self.cutter_diameter = 0
        total_cut_depth = (
            self.config.active_config.cutting_depths.material_thickness
            + self.config.active_config.cutting_depths.bottom_offset
        )

        def calculate_stepovers(start, stop, step):
            if step != 0:
                return [
                    round(start - i * step, 3)
                    for i in range(int((start - stop) / step) + 1)
                ]
            else:
                return [start]

        def rectangle_default_parameters(simulate=False):
            parameters = {
                "coordinates": coordinates,
                "datum_x": 0,
                "datum_y": 0,
                "offset": self.config.active_config.toolpath_offset,
                "tool_diameter": 0
                if self.cutter_diameter is None
                else self.cutter_diameter,
                "is_climb": is_climb,
                "corner_radius": self.config.active_config.canvas_shape_dims.r,
                "pass_depth": cutting_pass_depth,
                "feedrate": self.config.active_profile.cutting_parameters.max_feedrate,
                "plungerate": self.config.active_profile.cutting_parameters.plungerate,
                "total_cut_depth": total_cut_depth,
                "z_safe_distance": z_safe_distance,
                "pass_type": "Roughing pass",
                "simulate": simulate,
                "first_plunge": True,
            }
            if simulate:
                parameters["pass_depth"] = simulation_z_height
                parameters["feedrate"] = simulation_feedrate
                parameters["plungerate"] = simulation_plunge_rate
                parameters["total_cut_depth"] = simulation_z_height
            return parameters

        def circle_default_parameters(simulate=False):
            parameters = rectangle_default_parameters(simulate=simulate)
            parameters["corner_radius"] = (
                self.config.active_config.canvas_shape_dims.d / 2
            )
            return parameters

        def line_default_parameters(simulate=False):
            parameters = {
                "datum_x": 0,
                "datum_y": 0,
                "length": self.config.active_config.canvas_shape_dims.l,
                "tool_diameter": 0
                if self.cutter_diameter is None
                else self.cutter_diameter,
                "orientation": self.config.active_config.rotation,
                "pass_depth": self.config.active_config.cutting_depths.depth_per_pass,
                "feedrate": self.config.active_profile.cutting_parameters.max_feedrate,
                "plungerate": self.config.active_profile.cutting_parameters.plungerate,
                "total_cut_depth": total_cut_depth,
                "z_safe_distance": z_safe_distance,
                "simulate": simulate,
            }
            if simulate:
                parameters["pass_depth"] = simulation_z_height
                parameters["feedrate"] = simulation_feedrate
                parameters["plungerate"] = simulation_plunge_rate
                parameters["total_cut_depth"] = simulation_z_height
            return parameters

        shape_type = self.config.active_config.shape_type.lower()
        pocketing = self.config.active_config.toolpath_offset == "pocket"
        if shape_type in ["rectangle", "square"]:
            y_rect = self.config.active_config.canvas_shape_dims.y
            x_rect = (
                self.config.active_config.canvas_shape_dims.x
                if self.config.active_config.shape_type.lower()
                == ShapeOptions.RECTANGLE.value
                else self.config.active_config.canvas_shape_dims.y
            )
            rect_coordinates = self.rectangle_coordinates(x_rect, y_rect)
            if len(rect_coordinates) != 4:
                raise Exception(
                    "Sir, rectangles have 4 sides, not %d" % len(rect_coordinates)
                )
            coordinates = rect_coordinates
            coordinates.append(coordinates[0])
            length_to_cover_with_passes = 0
            if pocketing:
                length_to_cover_with_passes = min(x_rect, y_rect) / 2
            length_covered_by_finishing = (
                self.finishing_stepover * self.finishing_passes
            )
            length_to_cover_with_roughing = (
                length_to_cover_with_passes - length_covered_by_finishing
            )
            finishing_stepovers = calculate_stepovers(
                length_covered_by_finishing, 0, self.finishing_stepover
            )
            roughing_stepovers = calculate_stepovers(
                length_to_cover_with_roughing,
                finishing_stepovers[0],
                self.cutter_diameter / 2,
            )[1:]
            finishing_depths = self.calculate_pass_depths(
                total_cut_depth, self.finishing_stepdown
            )
            roughing_depths = self.calculate_pass_depths(
                total_cut_depth, cutting_pass_depth
            )
            if finishing_stepovers:
                roughing_stepovers.append(finishing_stepovers[0])
                finishing_stepovers = finishing_stepovers[1:]
            operations = {
                "Roughing": {
                    "stepovers": roughing_stepovers,
                    "cutting_depths": roughing_depths,
                },
                "Finishing": {
                    "stepovers": finishing_stepovers,
                    "cutting_depths": finishing_depths,
                },
            }
            if simulate:
                rectangle = self.cut_rectangle(
                    **rectangle_default_parameters(simulate=True)
                )
                cutting_lines += rectangle
            else:
                rectangle_parameters = rectangle_default_parameters()
                for operation_name, operation_data in operations.items():
                    for pass_depth in operation_data["cutting_depths"]:
                        for stepover in operation_data["stepovers"]:
                            first_plunge = stepover == operation_data["stepovers"][0]
                            rectangle_parameters["z_safe_distance"] = (
                                -1 * pass_depth + stepover_z_hop_distance
                            )
                            if self.cutter_diameter:
                                rectangle_parameters["tool_diameter"] = (
                                    self.cutter_diameter + stepover * 2
                                )
                            else:
                                rectangle_parameters["tool_diameter"] = 0
                            rectangle_parameters["total_cut_depth"] = pass_depth
                            rectangle_parameters["pass_depth"] = pass_depth
                            rectangle_parameters["pass_type"] = operation_name + " pass"
                            rectangle_parameters["first_plunge"] = first_plunge
                            rectangle = self.cut_rectangle(**rectangle_parameters)
                            rectangle = self.remove_redudant_lines(rectangle)
                            if (
                                not pocketing
                                and self.config.active_config.cutting_depths.tabs
                            ):
                                rectangle = self.tab_utils.add_tabs_to_gcode(
                                    rectangle,
                                    total_cut_depth,
                                    tab_height,
                                    tab_width,
                                    base_tab_spacing,
                                    self.cutter_diameter,
                                    three_d_tabs=three_d_tabs,
                                )
                            cutting_lines += rectangle
        elif shape_type in ["geberit"]:
            gcode_lines = self.find_and_read_gcode_file(
                self.source_folder_path,
                self.config.active_config.shape_type,
                self.cutter_diameter,
                orientation=self.config.active_config.rotation,
            )
            gcode_cut_depth, gcode_z_safe_distance = (
                self.extract_cut_depth_and_z_safe_distance(gcode_lines)
            )
            x_size, y_size, x_minus, y_minus = self.read_in_custom_shape_dimensions(
                gcode_lines
            )
            if simulate:
                coordinates = self.rectangle_coordinates(
                    float(x_size),
                    float(y_size) + self.cutter_diameter / 2,
                    float(x_minus),
                    float(y_minus),
                )
                coordinates.append(coordinates[0])
                rectangle_parameters = rectangle_default_parameters(simulate=True)
                rectangle_parameters["offset"] = "inside"
                rectangle_parameters["corner_radius"] = 0
                gcode_lines = self.cut_rectangle(**rectangle_parameters)
            else:
                gcode_lines = gcode_lines[
                    next(
                        (
                            i
                            for i, s in enumerate(gcode_lines)
                            if re.search("T[1-9]", s)
                        ),
                        None,
                    ) :
                ]
                gcode_lines = self.adjust_feeds_and_speeds(
                    gcode_lines,
                    self.config.active_profile.cutting_parameters.max_feedrate,
                    self.config.active_profile.cutting_parameters.plungerate,
                    self.config.active_profile.cutting_parameters.spindle_speed,
                )
                gcode_lines = self.replace_cut_depth_and_z_safe_distance(
                    gcode_lines,
                    gcode_cut_depth,
                    gcode_z_safe_distance,
                    "[cut depth] ",
                    z_safe_distance,
                )
                gcode_lines = self.apply_datum_offset(gcode_lines, 0, 0)
                pass_depths = self.calculate_pass_depths(
                    total_cut_depth,
                    self.config.active_config.cutting_depths.depth_per_pass,
                )
                start_condition = next(
                    (i for i, s in enumerate(gcode_lines) if re.search("M3", s)), None
                )
                end_condition = next(
                    (i for i, s in enumerate(gcode_lines) if re.search("M5", s)), None
                )
                gcode_lines = self.repeat_for_depths(
                    gcode_lines, pass_depths, start_condition, end_condition
                )
                tool_radius = self.cutter_diameter / 2
                if geberit_partoff:
                    partoff_start_coordinate = [
                        -1 * tool_radius + self.config.active_config.datum_position.x,
                        float(y_size)
                        + tool_radius
                        + self.config.active_config.datum_position.y,
                    ]
                    partoff_end_coordinate = [
                        tool_radius
                        + float(x_size)
                        + self.config.active_config.datum_position.x,
                        tool_radius
                        + float(y_size)
                        + self.config.active_config.datum_position.y,
                    ]
                    gcode_lines = self.add_partoff(
                        gcode_lines,
                        "M5",
                        partoff_start_coordinate,
                        partoff_end_coordinate,
                        pass_depths,
                        self.config.active_profile.cutting_parameters.max_feedrate,
                        self.config.active_profile.cutting_parameters.plungerate,
                        z_safe_distance,
                    )
            cutting_lines = gcode_lines
        elif shape_type in ["circle"]:
            circle_coordinates = self.rectangle_coordinates(
                self.config.active_config.canvas_shape_dims.d,
                self.config.active_config.canvas_shape_dims.d,
            )
            coordinates = circle_coordinates
            coordinates.append(coordinates[0])
            circle_radius = self.config.active_config.canvas_shape_dims.d / 2
            length_to_cover_with_passes = 0
            if pocketing:
                length_to_cover_with_passes = circle_radius
            length_covered_by_finishing = (
                self.finishing_stepover * self.finishing_passes
            )
            length_to_cover_with_roughing = (
                length_to_cover_with_passes - length_covered_by_finishing
            )
            finishing_stepovers = calculate_stepovers(
                length_covered_by_finishing, 0, self.finishing_stepover
            )
            roughing_stepovers = calculate_stepovers(
                length_to_cover_with_roughing,
                finishing_stepovers[0],
                self.cutter_diameter / 2,
            )[1:]
            finishing_depths = self.calculate_pass_depths(
                total_cut_depth, self.finishing_stepdown
            )
            roughing_depths = self.calculate_pass_depths(
                total_cut_depth, cutting_pass_depth
            )
            if finishing_stepovers:
                roughing_stepovers.append(finishing_stepovers[0])
                finishing_stepovers = finishing_stepovers[1:]
            operations = {
                "Roughing": {
                    "stepovers": roughing_stepovers,
                    "cutting_depths": roughing_depths,
                },
                "Finishing": {
                    "stepovers": finishing_stepovers,
                    "cutting_depths": finishing_depths,
                },
            }
            circle_parameters = circle_default_parameters(simulate=simulate)
            circle_parameters["datum_x"] = -1 * circle_radius
            circle_parameters["datum_y"] = -1 * circle_radius
            if simulate:
                circle_parameters["pass_depth"] = simulation_z_height
                circle_parameters["total_cut_depth"] = simulation_z_height
                circle_parameters["feedrate"] = simulation_feedrate
                circle_parameters["plungerate"] = simulation_plunge_rate
                circle = self.cut_rectangle(**circle_parameters)
                cutting_lines += circle
            else:
                for operation_name, operation_data in operations.items():
                    for pass_depth in operation_data["cutting_depths"]:
                        for stepover in operation_data["stepovers"]:
                            first_plunge = stepover == operation_data["stepovers"][0]
                            circle_parameters["z_safe_distance"] = (
                                -1 * pass_depth + stepover_z_hop_distance
                            )
                            if self.cutter_diameter:
                                circle_parameters["tool_diameter"] = (
                                    self.cutter_diameter + stepover * 2
                                )
                            else:
                                circle_parameters["tool_diameter"] = 0
                            circle_parameters["total_cut_depth"] = pass_depth
                            circle_parameters["pass_depth"] = pass_depth
                            circle_parameters["pass_type"] = operation_name + " pass"
                            circle_parameters["first_plunge"] = first_plunge
                            circle = self.cut_rectangle(**circle_parameters)
                            circle = self.remove_redudant_lines(circle)
                            if (
                                not pocketing
                                and self.config.active_config.cutting_depths.tabs
                            ):
                                circle = self.tab_utils.add_tabs_to_gcode(
                                    circle,
                                    total_cut_depth,
                                    tab_height,
                                    tab_width,
                                    base_tab_spacing,
                                    self.cutter_diameter,
                                    three_d_tabs=three_d_tabs,
                                )
                            cutting_lines += circle
        elif shape_type in ["line"]:
            cutting_lines = self.cut_line(**line_default_parameters(simulate=simulate))
        else:
            raise Exception(
                "Shape type: '%s' not supported" % self.config.active_config.shape_type
            )
        file_structure_1_shapes = ["rectangle", "square", "circle", "line"]
        if simulate:
            cutting_lines.insert(0, "G0 X0 Y0")
            cutting_lines.insert(0, "G90")
            cutting_lines.append(
                f"G0 X{-self.m.laser_offset_x_value} Y{-self.m.laser_offset_y_value}"
            )
            self.m.s.run_skeleton_buffer_stuffer(cutting_lines)
        else:
            if self.config.active_config.shape_type in file_structure_1_shapes:
                output = "(%s)\nG90\nG17\nM3 S%d\nG0 %s\n\n%s(End)\nG0 Z%d\nM5\n" % (
                    filename,
                    self.config.active_profile.cutting_parameters.spindle_speed,
                    safe_start_position,
                    "".join(cutting_lines),
                    z_safe_distance,
                )
            else:
                output = "(%s)\nG90\nG17\nM3 S%d\nG0 %s\n" % (
                    filename,
                    self.config.active_profile.cutting_parameters.spindle_speed,
                    safe_start_position,
                )
                output += "\n".join(cutting_lines)
            with open(output_path, "w+") as out_file:
                out_file.write(output)
                Logger.info("%s written" % filename)
                return output_path
