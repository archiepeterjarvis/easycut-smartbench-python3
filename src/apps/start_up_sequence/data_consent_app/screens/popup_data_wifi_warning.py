"""
@author Letty
Warning pop-up for data and consent app
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image


class PopupDataAndWiFiDisableWarning(Widget):
    def __init__(self, consent_manager, localization):
        self.c = consent_manager
        self.l = localization

        def decline_confirmed(*args):
            self.c.decline_terms_and_disable_wifi()

        description = (
            self.l.get_bold(
                "Are you sure you want to decline the data policy? This will disable the Console Wi-Fi."
            )
            + "\n\n"
            + self.l.get_str(
                "You can change your data preferences in the System Tools app at any time."
            )
        )
        title_string = (
            self.l.get_str("Warning!") + " " + self.l.get_str("Are you sure?")
        )
        ok_string = self.l.get_bold("Yes, disable Wi-Fi")
        back_string = self.l.get_bold("No, go back")
        img = Image(
            source="error_icon.png",
            allow_stretch=False,
        )
        label = Label(
            size_hint_y=1.3,
            text_size=(380, None),
            halign="center",
            valign="middle",
            text=description,
            color=[0, 0, 0, 1],
            padding=[0, 0],
            markup=True,
        )
        ok_button = Button(text=ok_string, markup=True)
        ok_button.background_normal = ""
        ok_button.background_color = [230 / 255.0, 74 / 255.0, 25 / 255.0, 1.0]
        back_button = Button(text=back_string, markup=True)
        back_button.background_normal = ""
        back_button.background_color = [76 / 255.0, 175 / 255.0, 80 / 255.0, 1.0]
        btn_layout = BoxLayout(
            orientation="horizontal", spacing=10, padding=[20, 0, 20, 0]
        )
        btn_layout.add_widget(back_button)
        btn_layout.add_widget(ok_button)
        layout_plan = BoxLayout(
            orientation="vertical", spacing=10, padding=[10, 20, 10, 20]
        )
        layout_plan.add_widget(img)
        layout_plan.add_widget(label)
        layout_plan.add_widget(btn_layout)
        popup = Popup(
            title=title_string,
            title_color=[0, 0, 0, 1],
            title_size="20sp",
            content=layout_plan,
            size_hint=(None, None),
            size=(500, 400),
            auto_dismiss=False,
        )
        popup.separator_color = [230 / 255.0, 74 / 255.0, 25 / 255.0, 1.0]
        popup.separator_height = "4dp"
        popup.background = "popup_background.png"
        ok_button.bind(on_press=popup.dismiss)
        ok_button.bind(on_press=decline_confirmed)
        back_button.bind(on_press=popup.dismiss)
        popup.open()
