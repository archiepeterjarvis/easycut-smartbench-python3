"""
@author: Archie

Popup system for easycut-smartbench
"""
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from enum import Enum

from asmcnc.skavaUI import utils


class PopupType(Enum):
    INFO = "./asmcnc/apps/shapeCutter_app/img/info_icon.png"
    ERROR = "./asmcnc/apps/shapeCutter_app/img/error_icon.png"
    OTHER = ""


class PopupSystem(Popup):
    sm = ObjectProperty(None)
    m = ObjectProperty(None)
    l = ObjectProperty(None)

    separator_color = [230 / 255., 74 / 255., 25 / 255., 1.]
    separator_height = 4
    background = StringProperty('./asmcnc/apps/shapeCutter_app/img/popup_background.png')
    auto_dismiss = ObjectProperty(False)

    """
    title_string: string to be used as title
    main_string: string to be used as main text
    popup_type: type of popup (enum)
    buttons: dictionary of button text and callback function
    popup_image: image to be used in popup (optional, defaults to the enum's image)
    """

    def __init__(self, title_string, main_string, popup_type, buttons,
                 popup_width=300, popup_height=300, popup_image=None,
                 dismiss_text="Ok", dismiss_callback=None, **kwargs):
        super(PopupSystem, self).__init__(**kwargs)

        self.title = self.l.get_str(title_string)
        self.size_hint = (None, None)
        self.width = dp(float(popup_width)/800.0)*Window.width
        self.height = dp(float(popup_height)/480.0)*Window.height

        self.main_string = self.l.get_str(main_string)
        self.buttons = buttons
        self.popup_type = popup_type
        self.popup_image = popup_image
        self.dismiss_text = dismiss_text
        self.dismiss_callback = dismiss_callback

        self.build()
        self.open()

    def build(self):
        image = Image(source=self.popup_type.value or self.popup_image)
        main_label = Label(size_hint_y=1, text_size=(utils.get_scaled_width(360), None), halign="center",
                           valign="middle", text=self.main_string, color=(0, 0, 0, 1), padding=(40, 20), markup=True)

        button_layout = self.build_button_layout()

        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=(40, 20))

        main_layout.add_widget(image)
        main_layout.add_widget(main_label)
        main_layout.add_widget(button_layout)

        self.content = main_layout

    def build_button_layout(self):
        button_layout = BoxLayout(orientation="horizontal", spacing=10, padding=0)
        for button in self.build_buttons():
            button_layout.add_widget(button)
        button_layout.add_widget(Button(text=self.dismiss_text, on_release=self.dismiss))
        return button_layout

    def on_dismiss(self, *args):
        if self.dismiss_callback is not None:
            self.dismiss_callback()

    def build_buttons(self):
        return [Button(text=self.l.get_bold(button_text), on_release=callback)
                for button_text, callback in self.buttons.items()]
