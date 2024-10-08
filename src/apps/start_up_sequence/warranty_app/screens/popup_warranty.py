"""
author: @Letty
module handles the warranty app popups
"""

import sys
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput


class QuitToConsoleWarranty(Widget):
    def __init__(self, screen_manager):
        self.systemtools_sm = screen_manager
        description = (
            """You should only quit to the console if you have been instructed to do so by YetiTool support.

"""
            + "This will take you to the YetiTool splash screen, and exit the software.\n\n"
            + "Would you like to quit to console now?"
        )

        def quit_console(*args):
            sys.exit()

        img = Image(
            source="error_icon.png",
            allow_stretch=False,
        )
        label = Label(
            size_hint_y=2,
            text_size=(360, None),
            halign="center",
            valign="middle",
            text=description,
            color=[0, 0, 0, 1],
            padding=[20, 0],
            markup=True,
        )
        ok_button = Button(text="[b]Yes[/b]", markup=True)
        ok_button.background_normal = ""
        ok_button.background_color = [76 / 255.0, 175 / 255.0, 80 / 255.0, 1.0]
        back_button = Button(text="[b]No[/b]", markup=True)
        back_button.background_normal = ""
        back_button.background_color = [230 / 255.0, 74 / 255.0, 25 / 255.0, 1.0]
        btn_layout = BoxLayout(
            orientation="horizontal", spacing=15, padding=[0, 5, 0, 0]
        )
        btn_layout.add_widget(back_button)
        btn_layout.add_widget(ok_button)
        layout_plan = BoxLayout(
            orientation="vertical", spacing=10, padding=[30, 20, 30, 0]
        )
        layout_plan.add_widget(img)
        layout_plan.add_widget(label)
        layout_plan.add_widget(btn_layout)
        popup = Popup(
            title="Warning!",
            title_color=[0, 0, 0, 1],
            title_size="20sp",
            content=layout_plan,
            size_hint=(None, None),
            size=(360, 360),
            auto_dismiss=False,
        )
        popup.separator_color = [230 / 255.0, 74 / 255.0, 25 / 255.0, 1.0]
        popup.separator_height = "4dp"
        popup.background = "popup_background.png"
        ok_button.bind(on_press=popup.dismiss)
        ok_button.bind(on_press=quit_console)
        back_button.bind(on_press=popup.dismiss)
        popup.open()


class PopupFactorySettingsPassword(Widget):
    def __init__(self, app_manager):
        self.am = app_manager
        description = (
            """You should only access the factory settings if you have been instructed to do so by YetiTool support.

"""
            + "Please enter the password to proceed."
        )

        def check_password(*args):
            if textinput.text == "Work Smart":
                self.am.systemtools_sm.open_system_tools()
                self.am.systemtools_sm.open_factory_settings_screen()

        img = Image(
            source="error_icon.png",
            allow_stretch=False,
        )
        label = Label(
            size_hint_y=1.2,
            text_size=(450, None),
            halign="center",
            valign="middle",
            text=description,
            color=[0, 0, 0, 1],
            padding=[0, 0],
            markup=True,
        )
        textinput = TextInput(size_hint_y=1, text="")
        ok_button = Button(text="[b]Ok[/b]", markup=True)
        ok_button.background_normal = ""
        ok_button.background_color = [230 / 255.0, 74 / 255.0, 25 / 255.0, 1.0]
        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, padding=[10, 0, 10, 0]
        )
        btn_layout.add_widget(ok_button)
        layout_plan = BoxLayout(
            orientation="vertical", spacing=5, padding=[40, 10, 40, 10]
        )
        layout_plan.add_widget(img)
        layout_plan.add_widget(label)
        layout_plan.add_widget(textinput)
        layout_plan.add_widget(btn_layout)
        popup = Popup(
            title="Warning!",
            title_color=[0, 0, 0, 1],
            title_size="20sp",
            content=layout_plan,
            size_hint=(None, None),
            size=(500, 320),
            auto_dismiss=False,
            pos_hint={"x": 150.0 / 800.0, "y": 160.0 / 480.0},
        )
        popup.separator_color = [230 / 255.0, 74 / 255.0, 25 / 255.0, 1.0]
        popup.separator_height = "4dp"
        popup.background = "popup_background.png"
        ok_button.bind(on_press=check_password)
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
