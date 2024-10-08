from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from core.localization import Localization
from ui.utils import scaling_utils
from ui.utils import color_provider


class ToolMaterialDisplayWidget(BoxLayout):
    padding = dp(3), dp(3), dp(3), dp(3)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.material_text = ""
        self.tool_text = ""
        self.l = Localization()
        background_color = color_provider.get_rgba("shapes_white")
        with self.canvas.before:
            Color(*background_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(pos=self.update_rect, size=self.update_rect)
        self.tool_material_label = Label(
            text="",
            halign="left",
            valign="top",
            font_size=scaling_utils.get_scaled_sp("13sp"),
            color=color_provider.get_rgba("black"),
            center_y=self.center_y,
        )
        self.tool_material_label.bind(size=self.tool_material_label.setter("text_size"))
        self.add_widget(self.tool_material_label)
        config.bind(active_profile=self.on_active_profile)
        self.on_active_profile(None)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_active_profile(self, *args):
        self.material_text = self.config.active_profile.material.description
        self.tool_text = self.get_translated_description(
            self.config.active_cutter.description
        )
        self.update_tool_material_label()

    def update_tool_material_label(self):
        self.tool_material_label.text = (
            self.l.get_str("Material")
            + ": "
            + self.l.get_str(self.material_text)
            + "\n"
            + self.l.get_str("Tool")
            + ":\n"
            + self.tool_text
        )

    def get_translated_description(self, material_description):
        desc = ""
        for elem in material_description.split(b" "):
            desc += self.l.get_str(elem) + " "
        return desc.strip()
