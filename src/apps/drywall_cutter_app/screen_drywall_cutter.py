import sys
import textwrap
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from core import paths
from apps.drywall_cutter_app import (
    screen_config_filechooser,
    widget_tool_material_display,
)
from apps.drywall_cutter_app import screen_config_filesaver
from apps.drywall_cutter_app import widget_drywall_shape_display
from apps.drywall_cutter_app import widget_xy_move_drywall
from apps.drywall_cutter_app.config import config_loader, config_options
from core.localization import Localization
from core.logging.logging_system import Logger
from apps.drywall_cutter_app import material_setup_popup
from apps.drywall_cutter_app import tool_material_popup
from apps.drywall_cutter_app import job_load_helper
from ui.utils import scaling_utils
from ui.popups.job_validation_popup import JobValidationPopup
from ui.popups import popup_info


class ImageButton(ButtonBehavior, Image):
    pass


from apps.drywall_cutter_app.engine import GCodeEngine

Builder.load_string(
    """
#:import ImageDropDownButton apps.drywall_cutter_app.image_dropdown
#:import color_provider ui.utils.color_provider

<DrywallCutterScreen>:
    shape_selection:shape_selection
    rotate_button:rotate_button
    toolpath_selection:toolpath_selection
    shape_display_container:shape_display_container
    xy_move_container:xy_move_container
    tool_material_display_container:tool_material_display_container
    right_side_container:right_side_container
    
    canvas.before:
        Color:
            rgba: color_provider.get_rgba('grey')
        Rectangle:
            size: self.size
            pos: self.pos
    
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            padding: dp(5)
            spacing: dp(10)
            ImageButton:
                source: 'home_button.png'
                allow_stretch: True
                size_hint_x: 7
                on_press: root.home()
            ImageButton:
                source: 'open_button.png'
                allow_stretch: True
                size_hint_x: 7
                text: 'File'
                on_press: root.open_filechooser()
            ImageButton:
                source: 'tool_and_material_button.png'
                allow_stretch: True
                size_hint_x: 7
                text: 'Tool & Material'
                on_press: root.tool_material_popup.open()
            ImageDropDownButton:
                id: shape_selection
                callback: root.select_shape
                image_dict: root.shape_options_dict
                key_name: 'key'
                size_hint_x: 7
                allow_stretch: True
                source: 'square_shape_button.png'
            ImageButton:
                id: rotate_button
                source: 'rotate_button.png'
                allow_stretch: True
                size_hint_x: 7
                text: 'Rotate'
                on_press: root.rotate_shape()
            ImageDropDownButton:
                id: toolpath_selection
                size_hint_x: 7
                callback: root.select_toolpath
                key_name: 'key'
                image_dict: root.toolpath_offset_options_dict
                allow_stretch: True
                source: 'toolpath_offset_inside_button.png'
            ImageButton:
                source: 'settings_button.png'
                allow_stretch: True
                size_hint_x: 7
                text: 'Material setup'
                text_size: self.size
                halign: 'center'
                valign: 'middle'
                on_press: root.material_setup()
            ImageButton:
                source: 'stop_button.png'
                allow_stretch: True
                size_hint_x: 15
                text: 'STOP'
                on_press: root.stop()
            ImageButton:
                source: 'exit_button.png'
                allow_stretch: True
                size_hint_x: 7
                on_press: root.quit_to_lobby()
                text: 'Quit'
        BoxLayout:
            size_hint_y: 5
            orientation: 'horizontal'
            padding: scaling_utils.get_scaled_tuple(dp(5), dp(5))
            spacing: scaling_utils.get_scaled_tuple(dp(10), dp(10))
            BoxLayout:
                id: shape_display_container
                size_hint_x: 55
            BoxLayout:
                id: right_side_container
                size_hint_x: 23
                orientation: 'vertical'
                spacing: dp(10)
                BoxLayout:
                    id: xy_move_container
                    size_hint_y: 23
                    padding: [dp(0), dp(0)]
                    canvas.before:
                        Color:
                            rgba: hex('#FFFFFFFF')
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    canvas.after:
                        Color:
                            rgba: (0, 0, 0, 0.5)
                        Line:
                            rectangle: self.x, self.y, self.width, self.height
                            width: 1
                BoxLayout:
                    id: tool_material_display_container
                    size_hint_y: 8
                    padding: [dp(0), dp(0)]
                    canvas.before:
                        Color:
                            rgba: hex('#FFFFFFFF')
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    canvas.after:
                        Color:
                            rgba: (0, 0, 0, 0.5)
                        Line:
                            rectangle: self.x, self.y, self.width, self.height
                            width: 1
                BoxLayout:
                    size_hint_y: 7
                    orientation: 'horizontal'
                    spacing: scaling_utils.get_scaled_tuple(dp(10), 0)
                    ImageButton:
                        source: 'simulate_button.png'
                        allow_stretch: True
                        text: 'Simulate'
                        on_press: root.simulate()
                    ImageButton:
                        source: 'save_button.png'
                        allow_stretch: True
                        text: 'Save'
                        on_press: root.save()
                    ImageButton:
                        source: 'go_button.png'
                        allow_stretch: True
                        text: 'Run'
                        on_press: root.run()
"""
)


class DrywallCutterScreen(Screen):
    shape_options = ["circle", "square", "rectangle", "line", "geberit"]
    line_cut_options = ["inside", "on", "outside"]
    rotation = "horizontal"
    current_pulse_opacity = 1
    shape_options_dict = {
        "circle": {"image_path": "circle_shape_button.png"},
        "square": {"image_path": "square_shape_button.png"},
        "line": {"image_path": "line_shape_button.png"},
        "geberit": {"image_path": "geberit_shape_button.png"},
        "rectangle": {"image_path": "rectangle_shape_button.png"},
    }
    toolpath_offset_options_dict = {
        "inside": {"image_path": "toolpath_offset_inside_button.png"},
        "outside": {"image_path": "toolpath_offset_outside_button.png"},
        "on": {"image_path": "toolpath_offset_on_button.png"},
        "pocket": {"image_path": "toolpath_offset_pocket_button.png"},
    }
    pulse_poll = None

    def __init__(self, screen_manager, machine, keyboard, job, **kwargs):
        self.dwt_config = config_loader.DWTConfig(self)
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.m = machine
        self.l = Localization()
        self.kb = keyboard
        self.jd = job
        self.pm = self.sm.pm
        self.cs = self.m.cs
        self.usm = App.get_running_app().user_settings_manager
        self.engine = GCodeEngine(self.m, self.dwt_config, self.cs)
        self.simulation_started = False
        self.ignore_state = True
        self.profile_db = App.get_running_app().profile_db
        self.xy_move_widget = widget_xy_move_drywall.XYMoveDrywall(
            machine=self.m,
            screen_manager=self.sm,
            localization=self.l,
            coordinate_system=self.cs,
        )
        self.xy_move_container.add_widget(self.xy_move_widget)
        self.materials_popup = material_setup_popup.CuttingDepthsPopup(
            self.l, self.kb, self.dwt_config
        )
        self.tool_material_popup = tool_material_popup.ToolMaterialPopup(
            self.l, self.dwt_config, self
        )
        self.drywall_shape_display_widget = (
            widget_drywall_shape_display.DrywallShapeDisplay(
                machine=self.m,
                screen_manager=self.sm,
                dwt_config=self.dwt_config,
                engine=self.engine,
                kb=self.kb,
                localization=self.l,
                cs=self.cs,
            )
        )
        self.shape_display_container.add_widget(self.drywall_shape_display_widget)
        self.xy_move_container.size_hint_y = 23
        self.tool_material_display_widget = (
            widget_tool_material_display.ToolMaterialDisplayWidget(self.dwt_config)
        )
        self.tool_material_display_container.add_widget(
            self.tool_material_display_widget
        )
        if self.dwt_config.app_type == config_options.AppType.SHAPES:
            self.drywall_shape_display_widget.canvas_image.source = paths.get_resource(
                "canvas_with_logo_shapes.png"
            )
        else:
            self.drywall_shape_display_widget.canvas_image.source = paths.get_resource(
                "canvas_with_logo_dwt.png"
            )
        self.show_toolpath_image()
        self.bumper_list = [
            self.drywall_shape_display_widget.bumper_bottom_image,
            self.drywall_shape_display_widget.bumper_right_image,
            self.drywall_shape_display_widget.bumper_top_image,
            self.drywall_shape_display_widget.bumper_left_image,
        ]
        self.dwt_config.bind(active_config=self.on_load_config)
        self.dwt_config.bind(active_profile=self.on_active_profile)
        self.m.bind(datum_position=self.set_datum_position)

    def set_datum_position(self, *args):
        if self.sm.current != self.name:
            return
        dx, dy = self.drywall_shape_display_widget.get_current_x_y(
            self.m.datum_position[0], self.m.datum_position[1], False
        )
        self.dwt_config.on_parameter_change("datum_position.x", dx)
        self.dwt_config.on_parameter_change("datum_position.y", dy)

    def on_pre_enter(self):
        self.apply_active_config()
        self.on_active_profile()
        self.materials_popup.on_open()
        self.pulse_poll = Clock.schedule_interval(self.update_pulse_opacity, 0.04)
        self.kb.set_numeric_pos(
            (scaling_utils.get_scaled_width(565), scaling_utils.get_scaled_height(115))
        )
        self.drywall_shape_display_widget.check_datum_and_extents()
        if self.dwt_config.app_type == config_options.AppType.SHAPES:
            if "geberit" in self.shape_options_dict:
                self.shape_options_dict.pop("geberit")
                self.shape_selection.image_dict = self.shape_options_dict
        if self.dwt_config.app_type == config_options.AppType.SHAPES:
            self.drywall_shape_display_widget.canvas_image.source = (
                "canvas_with_logo_shapes.png"
            )
        else:
            self.drywall_shape_display_widget.canvas_image.source = (
                "canvas_with_logo.png"
            )

    def on_enter(self):
        self.m.laser_on()

    def on_pre_leave(self):
        self.m.laser_off()
        if self.pulse_poll:
            Clock.unschedule(self.pulse_poll)
        self.kb.set_numeric_pos(None)

    def update_pulse_opacity(self, dt):
        if self.current_pulse_opacity <= 0:
            self.current_pulse_opacity = 0.01
        elif self.current_pulse_opacity >= 1:
            self.current_pulse_opacity = 0.98
        elif int(("%.2f" % self.current_pulse_opacity)[-1]) % 2 == 1:
            self.current_pulse_opacity += 0.1
        else:
            self.current_pulse_opacity -= 0.1
        for bumper in self.bumper_list:
            if "red" in bumper.source:
                bumper.opacity = self.current_pulse_opacity
            else:
                bumper.opacity = 1
        self.xy_move_widget.check_zh_at_datum(self.current_pulse_opacity)

    def home(self):
        self.m.request_homing_procedure("drywall_cutter", "drywall_cutter")

    def select_tool(self, cutter_file, *args):
        self.dwt_config.load_cutter(cutter_file)
        self.update_toolpaths()
        self.dwt_config.on_parameter_change("cutter_type", cutter_file)

    def on_active_profile(self, *args):
        if (
            self.dwt_config.active_config.material != "0010"
            or self.dwt_config.active_cutter.dimensions.tool_diameter not in [6, 8]
        ):
            if "geberit" in self.shape_options_dict:
                shapes_options = self.shape_options_dict.copy()
                shapes_options.pop("geberit")
                self.shape_selection.image_dict = shapes_options
        else:
            self.shape_selection.image_dict = self.shape_options_dict

    def update_toolpaths(self, *args):
        allowed_toolpaths = [
            toolpath
            for toolpath, allowed in self.dwt_config.active_cutter.generic_definition.toolpath_offsets.__dict__.items()
            if allowed
        ]
        allowed_toolpath_dict = {
            k: self.toolpath_offset_options_dict[k]
            for k in allowed_toolpaths
            if k in self.toolpath_offset_options_dict
        }
        self.toolpath_selection.image_dict = allowed_toolpath_dict
        if self.dwt_config.active_config.toolpath_offset not in allowed_toolpaths:
            self.select_toolpath(allowed_toolpaths[0])

    def select_shape(self, shape):
        self.dwt_config.on_parameter_change("shape_type", shape.lower())
        self.shape_selection.source = self.shape_options_dict[shape.lower()][
            "image_path"
        ]
        if shape in ["line", "geberit"]:
            self.toolpath_selection.disabled = True
            if self.dwt_config.active_config.toolpath_offset != "on":
                self.select_toolpath("on")
            else:
                self.drywall_shape_display_widget.select_toolpath(
                    self.dwt_config.active_config.shape_type, "on", self.rotation
                )
        else:
            self.select_toolpath(self.dwt_config.active_config.toolpath_offset)
            self.toolpath_selection.disabled = False
        if shape in ["rectangle", "line", "geberit"]:
            self.rotate_button.disabled = False
        else:
            self.rotate_button.disabled = True
        self.rotation = self.dwt_config.active_config.rotation
        self.drywall_shape_display_widget.select_shape(shape, self.rotation)
        if self.drywall_shape_display_widget.rotation_required():
            self.rotate_shape(swap_lengths=False)

    def rotate_shape(self, swap_lengths=True):
        if self.rotation == "horizontal":
            self.rotation = "vertical"
        else:
            self.rotation = "horizontal"
        self.drywall_shape_display_widget.select_shape(
            self.dwt_config.active_config.shape_type,
            self.rotation,
            swap_lengths=swap_lengths,
        )
        self.select_toolpath(self.dwt_config.active_config.toolpath_offset)
        self.drywall_shape_display_widget.swapping_lengths = True
        self.drywall_shape_display_widget.text_input_change(
            self.drywall_shape_display_widget.x_input
        )
        self.drywall_shape_display_widget.text_input_change(
            self.drywall_shape_display_widget.y_input
        )
        self.drywall_shape_display_widget.swapping_lengths = False

    def select_toolpath(self, toolpath):
        self.dwt_config.on_parameter_change("toolpath_offset", toolpath)
        self.drywall_shape_display_widget.select_toolpath(
            self.dwt_config.active_config.shape_type, toolpath, self.rotation
        )
        self.show_toolpath_image()

    def show_toolpath_image(self):
        self.toolpath_selection.source = self.toolpath_offset_options_dict[
            self.dwt_config.active_config.toolpath_offset
        ]["image_path"]

    def material_setup(self):
        self.materials_popup.open()

    def stop(self):
        popup_info.PopupStop(self.m, self.sm, self.l)

    def quit_to_lobby(self):
        self.set_return_screens()
        self.jd.reset_values()
        self.sm.current = "lobby"

    def simulate(self):
        self.drywall_shape_display_widget.defocus_inputs()
        self.popup_watchdog = Clock.schedule_interval(
            lambda dt: self.set_simulation_popup_state(self.m.s.m_state), 1
        )
        if not self.is_config_valid():
            self.show_validation_popup()
            return
        if not self.simulation_started and self.m.s.m_state.lower() == "idle":
            self.m.s.bind(
                m_state=lambda i, value: self.set_simulation_popup_state(value)
            )
            self.pm.show_wait_popup(
                main_string=self.l.get_str("Preparing for simulation") + "..."
            )
            self.ignore_state = False
            self.simulation_started = False
            self.engine.engine_run(simulate=True)

    def set_simulation_popup_state(self, machine_state):
        machine_state = machine_state.lower()
        if not self.ignore_state:
            if machine_state == "run":
                self.sm.pm.close_wait_popup()
                if not self.simulation_started:
                    self.sm.pm.show_simulating_job_popup()
                self.simulation_started = True
            elif (
                machine_state == "idle" or self.sm.current != "drywall_cutter"
            ) and self.simulation_started:
                self.sm.pm.close_simulating_job_popup()
                Clock.unschedule(self.popup_watchdog)
                self.simulation_started = False
                self.ignore_state = True
        if machine_state not in ["run", "idle"]:
            self.sm.pm.close_wait_popup()
            self.sm.pm.close_simulating_job_popup()
            Clock.unschedule(self.popup_watchdog)
            self.simulation_started = False
            self.ignore_state = True

    def save(self):
        self.drywall_shape_display_widget.defocus_inputs()
        if not self.is_config_valid():
            self.show_validation_popup()
            return
        if not self.sm.has_screen("config_filesaver"):
            self.sm.add_widget(
                screen_config_filesaver.ConfigFileSaver(
                    name="config_filesaver",
                    screen_manager=self.sm,
                    localization=self.l,
                    callback=self.dwt_config.save_config,
                    kb=self.kb,
                    dwt_config=self.dwt_config,
                )
            )
        self.sm.current = "config_filesaver"

    def is_config_valid(self):
        return (
            self.materials_popup.validate_inputs()
            and self.drywall_shape_display_widget.are_inputs_valid()
        )

    def run(self):
        self.drywall_shape_display_widget.defocus_inputs()
        if (
            self.materials_popup.validate_inputs()
            and self.drywall_shape_display_widget.are_inputs_valid()
        ):
            output_path = self.engine.engine_run()
            job_loader = job_load_helper.JobLoader(
                screen_manager=self.sm, machine=self.m, job=self.jd, localization=self.l
            )
            self.jd.set_job_filename(
                self.drywall_shape_display_widget.config_name_label.text
            )
            job_loader.load_gcode_file(output_path)
            self.set_return_screens()
            self.sm.get_screen("go").dwt_config = self.dwt_config
            self.proceed_to_go_screen()
        else:
            self.show_validation_popup()

    def show_validation_popup(self):
        m_popup_steps = self.materials_popup.get_steps_to_validate()
        s_widget_steps = self.drywall_shape_display_widget.get_steps_to_validate()
        m_popup_steps.extend(s_widget_steps)
        steps_to_validate = "\n".join(m_popup_steps)
        popup = JobValidationPopup(
            steps_to_validate, size_hint=(0.8, 0.8), auto_dismiss=False
        )
        popup.open()

    def set_return_screens(self):
        self.sm.get_screen("go").return_to_screen = (
            "drywall_cutter"
            if self.sm.get_screen("go").return_to_screen == "home"
            else "home"
        )
        self.sm.get_screen("go").cancel_to_screen = (
            "drywall_cutter"
            if self.sm.get_screen("go").cancel_to_screen == "home"
            else "home"
        )

    def proceed_to_go_screen(self):
        if self.jd.job_gcode == []:
            info = (
                self.format_command(
                    self.l.get_str("Before running, a file needs to be loaded.")
                )
                + "\n\n"
                + self.format_command(
                    self.l.get_str(
                        "Tap the file chooser in the first tab (top left) to load a file."
                    )
                )
            )
            popup_info.PopupInfo(self.sm, self.l, 450, info)
        elif (
            self.usm.get_value("dust_shoe_detection")
            and not self.m.s.dustshoe_is_closed
        ):
            self.sm.pm.show_dustshoe_warning_popup()
        elif self.m.is_machine_homed == False and sys.platform != "win32":
            self.m.request_homing_procedure("drywall_cutter", "drywall_cutter")
        elif (
            self.sm.get_screen("home").z_datum_reminder_flag
            or self.dwt_config.show_z_height_reminder
        ) and not self.sm.get_screen("home").has_datum_been_reset:
            z_datum_reminder_message = (
                self.format_command(
                    self.l.get_str(
                        "You may need to set a new Z datum before you start a new job!"
                    )
                )
                + "\n\n"
                + self.format_command(
                    self.l.get_str("Press Ok to clear this reminder.").replace(
                        self.l.get_str("Ok"), self.l.get_bold("Ok")
                    )
                )
            )
            popup_info.PopupWarning(self.sm, self.l, z_datum_reminder_message)
            self.sm.get_screen("home").z_datum_reminder_flag = False
            self.dwt_config.show_z_height_reminder = False
        else:
            self.jd.screen_to_return_to_after_job = "drywall_cutter"
            self.jd.screen_to_return_to_after_cancel = "drywall_cutter"
            self.m.stylus_router_choice = "router"
            if self.m.fw_can_operate_zUp_on_pause():
                self.sm.current = "lift_z_on_pause_or_not"
            else:
                self.sm.current = "jobstart_warning"

    def format_command(self, cmd):
        wrapped_cmd = textwrap.fill(cmd, width=35, break_long_words=False)
        return wrapped_cmd

    def open_filechooser(self):
        if not self.sm.has_screen("config_filechooser"):
            self.sm.add_widget(
                screen_config_filechooser.ConfigFileChooser(
                    name="config_filechooser",
                    screen_manager=self.sm,
                    localization=self.l,
                    callback=self.dwt_config.load_config,
                )
            )
        self.sm.current = "config_filechooser"

    def on_load_config(self, instance, value):
        """
        Called by the config_loader module when a config is loaded

        :return: None
        """
        Logger.debug("New config loaded. Applying settings.")
        self.apply_active_config()
        dx, dy = self.drywall_shape_display_widget.get_current_x_y(
            value.datum_position.x, value.datum_position.y, True
        )
        self.m.set_datum(x=dx, y=dy, relative=True)

    def apply_active_config(self):
        toolpath_offset = self.dwt_config.active_config.toolpath_offset
        rotation = self.dwt_config.active_config.rotation
        self.select_shape(self.dwt_config.active_config.shape_type)
        self.select_tool(self.dwt_config.active_config.cutter_type)
        self.select_toolpath(toolpath_offset)
        self.drywall_shape_display_widget.d_input.text = str(
            self.dwt_config.active_config.canvas_shape_dims.d
        )
        self.drywall_shape_display_widget.l_input.text = str(
            self.dwt_config.active_config.canvas_shape_dims.l
        )
        self.drywall_shape_display_widget.r_input.text = str(
            self.dwt_config.active_config.canvas_shape_dims.r
        )
        self.drywall_shape_display_widget.x_input.text = str(
            self.dwt_config.active_config.canvas_shape_dims.x
        )
        self.drywall_shape_display_widget.y_input.text = str(
            self.dwt_config.active_config.canvas_shape_dims.y
        )

    def on_leave(self, *args):
        self.dwt_config.save_temp_config()

    def format_command(self, cmd):
        wrapped_cmd = textwrap.fill(
            cmd, width=0.0625 * Window.width, break_long_words=False
        )
        return wrapped_cmd
