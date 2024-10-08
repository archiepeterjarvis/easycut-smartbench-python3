import math
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from ui.utils import scaling_utils

Builder.load_string(
    """
#:import FloatInput ui.components.text_inputs.float_input.FloatInput
<CuttingDepthsPopup>:
    float_layout:float_layout
    cutter_layout:cutter_layout
    
    material_graphic:material_graphic
    material_thickness:material_thickness
    bottom_offset:bottom_offset
    total_cut_depth:total_cut_depth
    depth_per_pass:depth_per_pass
    auto_pass_checkbox:auto_pass_checkbox
    tabs_checkbox:tabs_checkbox
    
    title_label:title_label
    material_thickness_label:material_thickness_label
    bottom_offset_label:bottom_offset_label
    total_cut_depth_label:total_cut_depth_label
    auto_pass_label:auto_pass_label
    depth_per_pass_label:depth_per_pass_label
    cut_depth_warning:cut_depth_warning
    pass_depth_warning:pass_depth_warning
    tabs_label:tabs_label
    
    cutter_graphic:cutter_graphic
    total_cut_depth_arrow:total_cut_depth_arrow
    
    confirm_button:confirm_button
    
    auto_dismiss: False
    size_hint: (None,None)
    size: (dp(app.get_scaled_width(577)), dp(app.get_scaled_height(301)))
    title: ''
    separator_height: 0
    background: 'cutting_depths_popup.png'
    
    FloatLayout:
        id: float_layout
        size_hint: (None, None)
        size: (dp(app.get_scaled_width(577)), dp(app.get_scaled_height(301)))
        pos_hint: {'y': -0.05}
                
        Label:
            id: title_label
            size_hint: None, None
            pos_hint: {'x': 0}
            text: 'Cutting depths'
            font_size: app.get_scaled_sp('20sp')
            color: hex('#F9F9F9')
            size: self.texture_size
        
        Label:
            id: Z0
            pos_hint: {'x': 0.0375, 'y': 0.21}
            text: 'Z0'
            font_size: app.get_scaled_sp('20sp')
            color: hex('#333333')
            
        Image:
            id: material_graphic
            source: "material_graphic.png"
            pos_hint: {'center_x': 0.45}
            y: self.parent.y
            size: self.parent.size
            allow_stretch: True 
        
        Label:
            id: material_thickness_label
            pos_hint: {'x': -0.42, 'y': 0.23}
            text: ''
            font_size: app.get_scaled_sp('16sp')
            color: hex('#333333')
            text_size: (dp(app.get_scaled_width(80)), None)
            
        Image:
            id: material_thickness_dims
            source: "material_thickness_dims.png"
            pos_hint: {'center_x': 0.45}
            y: self.parent.y
            size: self.parent.size
            allow_stretch: True
            
        FloatInput:
            id: material_thickness
            pos_hint: {'x': 0.165, 'y': 0.68}
            padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
            halign: 'center'
            size_hint: (.12, .1)
            text_size: self.size
            font_size: app.get_scaled_sp('16sp')
            markup: True
            multiline: False
            text: ''
        
        Label:
            id: bottom_offset_label
            pos_hint: {'x': -0.42, 'y': -0.075}
            text: ''
            font_size: app.get_scaled_sp('16sp')
            color: hex('#333333')
            text_size: (dp(app.get_scaled_width(80)), None)
            
        Image:
            id: bottom_offset_graphic
            source: "bottom_offset_graphic.png"
            pos_hint: {'center_x': 0.45}
            y: self.parent.y
            size: self.parent.size
            allow_stretch: True
        
        FloatInput:
            id: bottom_offset
            pos_hint: {'x': 0.165, 'y': 0.37}
            padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
            halign: 'center'
            size_hint: (.12, .1)
            text_size: self.size
            font_size: app.get_scaled_sp('16sp')
            markup: True
            multiline: False
            text: ''
            positive_only: False
        
        Image:
            id: total_cut_depth_dims
            source: "total_cut_depth_dims.png"
            pos_hint: {'center_x': 0.45}
            y: self.parent.y
            size: self.parent.size
            allow_stretch: True
        
        Label:
            id: total_cut_depth_label
            pos_hint: {'x': -0.42, 'y': -0.275}
            text: ''
            font_size: app.get_scaled_sp('16sp')
            color: hex('#333333')
            text_size: (dp(app.get_scaled_width(80)), None)
            
        FloatInput:
            id: total_cut_depth
            pos_hint: {'x': 0.165, 'y': 0.165}
            padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
            halign: 'center'
            size_hint: (.12, .1)
            text_size: self.size
            font_size: app.get_scaled_sp('16sp')
            markup: True
            multiline: False
            text: ''
            disabled: True
            
        StencilView:  # Prevents the images from going off the popup
            size: self.parent.size
            pos: self.parent.pos
            
            FloatLayout:
                id: cutter_layout
                size: self.parent.size
                pos: self.parent.pos
                
                Image:
                    id: total_cut_depth_arrow
                    source: "total_cut_depth_bottom_arrow.png"
                    pos_hint: {'center_x': 0.45, 'y': 0.225}
                    y: self.parent.y
                    size: self.parent.size
                    allow_stretch: True
                
                Image:
                    id: cutter_graphic
                    source: "cutter_graphic.png"
                    pos_hint: {'center_x': 0.45, 'y': 0.225}
                    # y: self.parent.y
                    size: self.parent.size
                    allow_stretch: True 
        
        Label:
            id: cut_depth_warning
            pos_hint: {'x': -0.335, 'y': -0.4}
            text: ''
            font_size: app.get_scaled_sp('14sp')
            markup: True
            color: hex('#FF0000')
            text_size: (dp(app.get_scaled_width(180)), None)
        
        Label:
            id: pass_depth_warning
            pos_hint: {'x': 0.2525, 'y': -0.225}
            text: ''
            font_size: app.get_scaled_sp('14sp')
            markup: True
            color: hex('#FF0000')
            text_size: (dp(app.get_scaled_width(180)), None) 
        
        GridLayout:
            rows: 3
            cols: 2
            pos_hint: {'x': 0.6, 'y': -0.1}
            row_force_default: True
            col_force_default: True
            row_default_height: dp(app.get_scaled_height(55))
            col_default_width: dp(app.get_scaled_width(100))
            
            Label:
                id: tabs_label
                text: ''
                font_size: app.get_scaled_sp('16sp')
                color: hex('#333333')
                text_size: (dp(app.get_scaled_width(100)), None)
            
            CheckBox:
                id: tabs_checkbox
                size_hint: (0.3,1)
                active: True
                background_checkbox_normal: "checkbox_inactive.png"
            
            Label:
                id: auto_pass_label
                text: ''
                font_size: app.get_scaled_sp('16sp')
                color: hex('#333333')
                text_size: (dp(app.get_scaled_width(100)), None)
            
            CheckBox:
                id: auto_pass_checkbox
                size_hint: (0.3,1)
                active: True
                background_checkbox_normal: "checkbox_inactive.png"
                on_active: root.on_auto_pass_checkbox()
            
            Label:
                id: depth_per_pass_label
                text: ''
                font_size: app.get_scaled_sp('16sp')
                color: hex('#333333')
                text_size: (dp(app.get_scaled_width(100)), None)
                
            FloatInput:
                id: depth_per_pass
                padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
                halign: 'center'
                size_hint: (None, None)
                size: (dp(app.get_scaled_width(100)), dp(app.get_scaled_height(45)))
                text_size: self.size
                font_size: app.get_scaled_sp('16sp')
                markup: True
                multiline: False
                text: ''
                disabled: True
                
        BoxLayout:
            orientation: 'horizontal'
            pos_hint: {'x': 0.625, 'y': 0.075}
            size_hint: (None, None)
            size: (dp(app.get_scaled_width(189)),dp(app.get_scaled_height(23)))
            spacing: dp(app.get_scaled_width(20))

            Button:
                id: cancel_button
                on_press: root.cancel()
                size_hint: (None,None)
                width: dp(app.get_scaled_width(83))
                height: dp(app.get_scaled_height(23))
                background_color: [0,0,0,0]
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "cancel_button.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True

            Button:
                id: confirm_button
                on_press: root.confirm()
                size_hint: (None,None)
                width: dp(app.get_scaled_width(86))
                height: dp(app.get_scaled_height(23))
                background_color: [0,0,0,0]
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "confirm_button.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
        
"""
)


class CuttingDepthsPopup(Popup):
    soft_limit_total_cut_depth = 62

    def __init__(self, localization, keyboard, dwt_config, **kwargs):
        super().__init__(**kwargs)
        self.l = localization
        self.kb = keyboard
        self.dwt_config = dwt_config
        self.pass_depth_lines = []
        self.float_layout.remove_widget(self.cut_depth_warning)
        self.float_layout.remove_widget(self.pass_depth_warning)
        self.refs = [self.cut_depth_warning.__self__, self.pass_depth_warning.__self__]
        self.text_inputs = [
            self.material_thickness,
            self.bottom_offset,
            self.total_cut_depth,
            self.depth_per_pass,
        ]
        self.kb.setup_text_inputs(self.text_inputs)
        for text_input in self.text_inputs:
            text_input.bind(focus=self.text_on_focus)
        self.depth_per_pass.bind(text=self.warning_pass_depth)
        self.cut_depth_warning.bind(parent=self.schedule_disable_confirm_button)
        self.pass_depth_warning.bind(parent=self.schedule_disable_confirm_button)
        self.dwt_config.bind(active_profile=self.on_open)
        self.update_strings()

    def update_error_messages(self):
        self.pass_depth_warning_cutter_max = (
            "[color=#FF0000]"
            + self.l.get_str("Max depth per pass for this tool is")
            + " Xmm[/color]".replace(
                "X",
                str(
                    self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
                ),
            )
        )
        self.pass_depth_warning_zero = (
            "[color=#FF0000]"
            + self.l.get_str("Depth per pass must be greater than 0")
            + "[/color]"
        )
        self.cut_depth_warning_soft_limit = (
            "[color=#FF0000]"
            + self.l.get_str("Max allowable cut is")
            + " Xmm[/color]".replace("X", str(self.soft_limit_total_cut_depth))
        )
        self.cut_depth_warning_cutter_max = (
            "[color=#FF0000]"
            + self.l.get_str("Max depth of tool is")
            + " Xmm[/color]".replace(
                "X", str(self.dwt_config.active_cutter.flutes.lengths.total)
            )
        )
        self.cut_depth_warning_zero = (
            "[color=#FF0000]"
            + self.l.get_str("Total cut depth must be greater than 0")
            + "[/color]"
        )

    def on_open(self, *args):
        self.title_label.pos_hint["x"] = 0
        if scaling_utils.Width == 800:
            self.title_label.pos_hint["y"] = 0.9
        else:
            self.title_label.pos_hint["y"] = 0.93
        self.update_strings()
        self.load_active_config()
        self.update_text()
        self.on_auto_pass_checkbox()

    def get_safe_float(self, val):
        try:
            return float(val)
        except:
            return 0.0

    def text_on_focus(self, instance, value):
        if not value:
            self.update_text()

    def schedule_disable_confirm_button(self, *args):
        Clock.schedule_once(self.disable_confirm_button)

    def load_active_config(self):
        self.material_thickness.text = str(
            self.dwt_config.active_config.cutting_depths.material_thickness
        )
        self.bottom_offset.text = str(
            self.dwt_config.active_config.cutting_depths.bottom_offset
        )
        self.auto_pass_checkbox.active = (
            self.dwt_config.active_config.cutting_depths.auto_pass
        )
        self.tabs_checkbox.active = self.dwt_config.active_config.cutting_depths.tabs
        self.depth_per_pass.text = str(
            self.dwt_config.active_config.cutting_depths.depth_per_pass
        )
        self.update_text()

    def update_strings(self):
        self.update_error_messages()
        self.title_label.text = self.l.get_str("Cutting depths")
        self.material_thickness_label.text = self.l.get_str("Material thickness")
        self.bottom_offset_label.text = self.l.get_str("Bottom offset")
        self.total_cut_depth_label.text = self.l.get_str("Total cut depth")
        self.tabs_label.text = self.l.get_str("Tabs")
        self.auto_pass_label.text = self.l.get_str("Auto pass depth")
        self.depth_per_pass_label.text = self.l.get_str("Depth per pass")
        self.pass_depth_warning.text = self.pass_depth_warning_cutter_max
        self.cut_depth_warning.text = self.cut_depth_warning_soft_limit

    def on_auto_pass_checkbox(self):
        if self.auto_pass_checkbox.active:
            self.depth_per_pass.disabled = True
            self.depth_per_pass.text = str(
                self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
            )
            self.update_animations()
        else:
            self.depth_per_pass.disabled = False
            self.depth_per_pass.hint_text = self.depth_per_pass.text

    def update_cutter_position(self):
        upper_limit = 0.225
        lower_limit = -0.035
        range = upper_limit - lower_limit
        bottom_offset = self.get_safe_float(self.bottom_offset.text)
        material_thickness = self.get_safe_float(self.material_thickness.text)
        ratio = 0 if material_thickness == 0 else bottom_offset / material_thickness
        cutter_y = lower_limit - range * ratio
        self.cutter_graphic.pos_hint["y"] = cutter_y
        self.total_cut_depth_arrow.pos_hint["y"] = cutter_y
        self.float_layout.do_layout()
        self.cutter_layout.do_layout()

    def update_text(self):
        cutter_max_depth_total = self.dwt_config.active_cutter.flutes.lengths.total
        if self.soft_limit_total_cut_depth < cutter_max_depth_total:
            max_cut_depth = self.soft_limit_total_cut_depth
            self.cut_depth_warning.text = self.cut_depth_warning_soft_limit
        else:
            max_cut_depth = cutter_max_depth_total
            self.cut_depth_warning.text = self.cut_depth_warning_cutter_max
        material_thickness = self.get_safe_float(self.material_thickness.text)
        bottom_offset = self.get_safe_float(self.bottom_offset.text)
        if material_thickness < 0:
            self.material_thickness.text = "0"
            material_thickness = 0
        if abs(bottom_offset) > material_thickness:
            if bottom_offset < 0:
                if self.material_thickness.text == "":
                    self.bottom_offset.text = ""
                    bottom_offset = material_thickness
                else:
                    self.bottom_offset.text = "-" + self.material_thickness.text
                    bottom_offset = -material_thickness
        self.total_cut_depth.text = str(material_thickness + bottom_offset)
        if self.cut_depth_warning not in self.float_layout.children:
            self.float_layout.add_widget(self.cut_depth_warning)
        if float(self.total_cut_depth.text) > max_cut_depth:
            self.cut_depth_warning.text = self.cut_depth_warning_cutter_max
        elif float(self.total_cut_depth.text) <= 0:
            self.cut_depth_warning.text = self.cut_depth_warning_zero
        else:
            self.float_layout.remove_widget(self.cut_depth_warning)
        self.update_animations()

    def update_animations(self):
        if (
            self.cut_depth_warning not in self.float_layout.children
            and self.pass_depth_warning not in self.float_layout.children
        ):
            self.update_cutter_position()
            self.calculate_depth_per_pass()

    def warning_pass_depth(self, *args):
        if self.auto_pass_checkbox.active:
            depth_per_pass = self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
            if self.pass_depth_warning not in self.float_layout.children:
                self.float_layout.add_widget(self.pass_depth_warning)
            if depth_per_pass <= 0:
                self.pass_depth_warning.text = self.pass_depth_warning_zero
            else:
                self.float_layout.remove_widget(self.pass_depth_warning)
        else:
            depth_per_pass = self.get_safe_float(self.depth_per_pass.text)
            if self.pass_depth_warning not in self.float_layout.children:
                self.float_layout.add_widget(self.pass_depth_warning)
            if (
                depth_per_pass
                > self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
            ):
                self.pass_depth_warning.text = self.pass_depth_warning_cutter_max
            elif depth_per_pass <= 0:
                self.pass_depth_warning.text = self.pass_depth_warning_zero
            else:
                self.float_layout.remove_widget(self.pass_depth_warning)

    def disable_confirm_button(self, *args):
        children = self.float_layout.children
        if self.cut_depth_warning in children or self.pass_depth_warning in children:
            self.confirm_button.disabled = True
            self.confirm_button.opacity = 0.5
        else:
            self.confirm_button.disabled = False
            self.confirm_button.opacity = 1
        self.float_layout.do_layout()

    def generate_pass_depth_lines(self, number_of_passes):
        upper_limit = 0.0825
        lower_limit = -0.175
        line_range = upper_limit - lower_limit
        material_thickness = self.get_safe_float(self.material_thickness.text)
        depth_per_pass = self.get_safe_float(self.depth_per_pass.text)
        ratio = 0 if material_thickness == 0 else depth_per_pass / material_thickness
        singular_cut = (
            0 if self.depth_per_pass.text == "" else round(ratio * line_range, 4)
        )
        for pass_line in self.pass_depth_lines:
            self.cutter_layout.remove_widget(pass_line)
        if self.total_cut_depth.text != "0.0":
            for i in range(0, int(number_of_passes)):
                line_depth = upper_limit - singular_cut * (i + 1)
                cutter_limit = lower_limit - (
                    -0.035 - self.cutter_graphic.pos_hint["y"]
                )
                if line_depth < cutter_limit:
                    line_depth = cutter_limit
                img = Image(
                    source="pass_depth_line.png",
                    allow_stretch=True,
                    pos_hint={"center_x": 0.45, "y": line_depth},
                )
                self.cutter_layout.add_widget(img)
                self.pass_depth_lines.append(img)
        self.cutter_layout.do_layout()

    def calculate_depth_per_pass(self):
        max_cut_depth_per_pass = (
            self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
        )
        if self.auto_pass_checkbox.active:
            depth_per_pass = max_cut_depth_per_pass
            number_of_passes = (
                0
                if depth_per_pass == 0
                else math.ceil(
                    self.get_safe_float(self.total_cut_depth.text) / depth_per_pass
                )
            )
            if depth_per_pass > max_cut_depth_per_pass:
                self.depth_per_pass.text = str(max_cut_depth_per_pass)
            else:
                self.depth_per_pass.text = str(round(depth_per_pass, 3))
            self.generate_pass_depth_lines(number_of_passes)
        else:
            depth_per_pass = self.get_safe_float(self.depth_per_pass.text)
            number_of_passes = (
                0
                if depth_per_pass == 0
                else math.ceil(
                    self.get_safe_float(self.total_cut_depth.text) / depth_per_pass
                )
            )
            self.generate_pass_depth_lines(number_of_passes)

    def confirm(self):
        self.kb.defocus_all_text_inputs(self.text_inputs)
        material_thickness = self.get_safe_float(self.material_thickness.text)
        bottom_offset = self.get_safe_float(self.bottom_offset.text)
        depth_per_pass = self.get_safe_float(self.depth_per_pass.text)
        self.dwt_config.on_parameter_change(
            "cutting_depths.material_thickness", material_thickness
        )
        self.dwt_config.on_parameter_change(
            "cutting_depths.bottom_offset", bottom_offset
        )
        self.dwt_config.on_parameter_change(
            "cutting_depths.depth_per_pass", depth_per_pass
        )
        self.dwt_config.on_parameter_change(
            "cutting_depths.auto_pass", self.auto_pass_checkbox.active
        )
        self.dwt_config.on_parameter_change(
            "cutting_depths.tabs", self.tabs_checkbox.active
        )
        self.dismiss()

    def cancel(self):
        self.kb.defocus_all_text_inputs(self.text_inputs)
        self.load_active_config()
        self.dismiss()

    def validate_inputs(self):
        material_thickness = self.get_safe_float(self.material_thickness.text)
        bottom_offset = self.get_safe_float(self.bottom_offset.text)
        total_cut_depth = self.get_safe_float(self.total_cut_depth.text)
        depth_per_pass = self.get_safe_float(self.depth_per_pass.text)
        auto_pass_checkbox = self.auto_pass_checkbox.active
        max_cut_depth_per_pass = (
            self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
        )
        if material_thickness < 0:
            return False
        if abs(bottom_offset) > material_thickness:
            if bottom_offset < 0:
                return False
        if (
            total_cut_depth < 0
            or total_cut_depth > self.soft_limit_total_cut_depth
            or total_cut_depth > self.dwt_config.active_cutter.flutes.lengths.total
        ):
            return False
        if total_cut_depth != material_thickness + bottom_offset:
            return False
        if depth_per_pass > max_cut_depth_per_pass or depth_per_pass <= 0:
            return False
        return True

    def get_steps_to_validate(self):
        steps = []
        material_thickness = (
            0
            if self.material_thickness.text == "" or self.material_thickness.text == "-"
            else float(self.material_thickness.text)
        )
        bottom_offset = (
            0
            if self.bottom_offset.text == "" or self.bottom_offset.text == "-"
            else float(self.bottom_offset.text)
        )
        total_cut_depth = (
            0
            if self.total_cut_depth.text == "" or self.total_cut_depth.text == "-"
            else float(self.total_cut_depth.text)
        )
        depth_per_pass = (
            0
            if self.depth_per_pass.text == "" or self.depth_per_pass.text == "-"
            else float(self.depth_per_pass.text)
        )
        max_cut_depth_per_pass = (
            self.dwt_config.active_profile.cutting_parameters.recommendations.stepdown
        )
        if material_thickness < 0:
            steps.append(
                self.l.get_str("Material thickness cannot be negative.")
                + "\n\n"
                + self.l.get_bold("Try increasing the material thickness.")
                + "\n\n"
            )
        if abs(bottom_offset) > material_thickness:
            if bottom_offset < 0:
                steps.append(
                    self.l.get_str(
                        "Bottom offset cannot be greater than material thickness"
                    )
                    + "\n\n"
                    + self.l.get_bold(
                        "Try reducing the bottom offset, or increasing the material thickness."
                    )
                    + "\n\n"
                )
        if total_cut_depth < 0:
            steps.append(
                self.l.get_str("Total cut depth cannot be negative")
                + "\n\n"
                + self.l.get_bold(
                    "Try reducing the bottom offset, or increasing the material thickness."
                )
                + "\n\n"
            )
        if total_cut_depth > self.soft_limit_total_cut_depth:
            steps.append(
                self.l.get_str("Total cut depth exceeds 62mm")
                + "\n\n"
                + self.l.get_bold(
                    "Try increasing the bottom offset, or reducing the material thickness."
                )
                + "\n\n"
            )
        if total_cut_depth != material_thickness + bottom_offset:
            steps.append(
                self.l.get_str(
                    "Total cut depth must be equal to material thickness + bottom offset."
                )
                + "\n\n"
            )
        if depth_per_pass > max_cut_depth_per_pass:
            steps.append(
                self.l.get_str(
                    "Depth per pass exceeds max depth per pass for this tool."
                )
                + "\n\n"
                + self.l.get_bold(
                    "Try reducing the depth per pass, or use a different tool."
                )
                + "\n\n"
            )
        if depth_per_pass <= 0:
            steps.append(
                self.l.get_str("Depth per pass must be positive.")
                + "\n\n"
                + self.l.get_bold(
                    "Try increasing the depth per pass, or use auto pass."
                )
                + "\n\n"
            )
        if total_cut_depth > self.dwt_config.active_cutter.flutes.lengths.total:
            steps.append(
                self.l.get_str("Total cut depth exceeds max depth of tool.")
                + "\n\n"
                + self.l.get_bold(
                    "Try reducing the total cut depth, or use a different tool."
                )
                + "\n\n"
            )
        return steps
