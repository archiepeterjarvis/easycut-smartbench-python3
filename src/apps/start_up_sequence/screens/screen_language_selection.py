import os
from functools import partial
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from core import paths
from core.localization import Localization
from core.managers.model_manager import ModelManagerSingleton
from ui.utils import color_provider

FLAGS_PATH = os.path.join(paths.SKAVA_UI_IMG_PATH, "flags")
WELCOME_STRINGS = [
    "Welcome to SmartBench",
    "Willkommen bei SmartBench",
    "Benvenuto in Smartbench",
    "Benvenuti in Smartbench",
    "Tervetuloa Smartbenchiin",
    "Witamy w SmartBench",
    "Velkommen til SmartBench",
    "PLACEHOLDER",
]


def get_language_flag_path(language):
    flag_name = language.split("(")[1][:-1].lower()
    return os.path.join(FLAGS_PATH, flag_name + ".png")


class LanguageSelectionScreen(Screen):
    def __init__(self, screen_manager, start_seq, **kwargs):
        super().__init__(**kwargs)
        self.model_manager = ModelManagerSingleton()
        self.localisation = Localization()
        self.language_chosen = ""
        self.update_welcome_label_clock = None
        self.update_language_index = 0
        self.screen_manager = screen_manager
        self.start_seq = start_seq
        self.root_layout = BoxLayout(orientation="vertical")
        self.header = BoxLayout(size_hint=(1, 800.0 / 60.0 / 100.0))
        self.header.bind(size=self.__update_header, pos=self.__update_header)
        self.welcome_label = Label(
            text=self.localisation.get_str(WELCOME_STRINGS[0]),
            font_size="30sp",
            color=color_provider.get_rgba("white"),
        )
        self.header.add_widget(self.welcome_label)
        self.body = BoxLayout(size_hint=(1, 0.55))
        self.body.bind(size=self.__update_body, pos=self.__update_body)
        self.language_flags_container = GridLayout(
            cols=3, size_hint=(0.8, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        for language in self.localisation.approved_languages:
            localisation_choice_option = self.__get_language_option_widget(language)
            if (
                self.model_manager.is_machine_drywall()
                and language not in self.localisation.dwt_languages
            ):
                localisation_choice_option.opacity = 0
            self.language_flags_container.add_widget(localisation_choice_option)
        self.body.add_widget(self.language_flags_container)
        self.footer = BoxLayout(size_hint=(1, 0.35))
        self.footer.bind(size=self.__update_footer, pos=self.__update_footer)
        next_string = self.localisation.get_str("Next") + "..."
        spacer = Label(text="", size_hint=(0.3, 0.8))
        self.next_button = Button(
            text=next_string,
            size_hint=(None, None),
            width=dp(291),
            height=dp(79),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            disabled=True,
            font_size="30sp",
            opacity=0,
            background_down=os.path.join(paths.SKAVA_UI_IMG_PATH, "next.png"),
            background_normal=os.path.join(paths.SKAVA_UI_IMG_PATH, "next.png"),
            on_press=self.__next_button_pressed,
        )
        spacer2 = Label(text="", size_hint=(0.3, 0.8))
        self.footer.add_widget(spacer)
        self.footer.add_widget(self.next_button)
        self.footer.add_widget(spacer2)
        self.root_layout.add_widget(self.header)
        self.root_layout.add_widget(self.body)
        self.root_layout.add_widget(self.footer)
        self.add_widget(self.root_layout)

    def on_enter(self, *args):
        self.update_welcome_label_clock = Clock.schedule_interval(
            self.__update_welcome_label, 1
        )

    def on_leave(self, *args):
        self.update_welcome_label_clock.cancel()

    def __update_welcome_label(self, *args):
        self.update_language_index += 1
        self.update_language_index %= len(WELCOME_STRINGS)
        if self.update_language_index == 7:
            self.welcome_label.font_name = self.localisation.korean_font
        else:
            self.welcome_label.font_name = self.localisation.font_regular
        self.welcome_label.text = self.localisation.get_str(
            WELCOME_STRINGS[self.update_language_index]
        )

    def __next_button_pressed(self, *args):
        for screen_name in self.start_seq.screen_sequence + ["rebooting"]:
            screen = self.screen_manager.get_screen(screen_name)
            if hasattr(screen, "update_strings"):
                screen.update_strings()
            for widget in screen.walk():
                if isinstance(widget, Label):
                    widget.font_name = self.localisation.font_regular
        self.start_seq.next_in_sequence()

    def __get_language_option_widget(self, language):
        root_layout = GridLayout(
            cols=3, rows=1, spacing=dp(10), padding=[dp(20), 0, 0, 0]
        )
        check_box = CheckBox(
            color=color_provider.get_rgba("dark_grey"),
            size_hint=(None, None),
            width=dp(30),
            group="language_selection",
            on_press=partial(self.__on_language_selected, language),
        )
        flag_path = get_language_flag_path(language)
        flag_image = Image(
            source=flag_path, allow_stretch=True, size_hint=(None, None), width=dp(50)
        )
        language_label = Label(
            text=language,
            color=color_provider.get_rgba("black"),
            valign="middle",
            halign="left",
        )
        if flag_path.endswith("ko.png"):
            language_label.font_name = self.localisation.korean_font
        language_label.bind(size=language_label.setter("text_size"))
        root_layout.add_widget(check_box)
        root_layout.add_widget(flag_image)
        root_layout.add_widget(language_label)
        return root_layout

    def __on_language_selected(self, language, instance):
        if instance.parent.opacity == 0 or not instance.active:
            self.language_chosen = ""
            self.next_button.disabled = True
            self.next_button.opacity = 0
            return
        instance.color = color_provider.get_rgba("blue")
        self.language_chosen = language
        self.next_button.disabled = False
        self.next_button.opacity = 1
        if language == self.localisation.ko:
            self.welcome_label.font_name = self.localisation.korean_font
            self.next_button.font_name = self.localisation.korean_font
        self.localisation.load_in_new_language(language)
        self.next_button.text = self.localisation.get_str("Next") + "..."

    def __update_body(self, *args):
        self.body.canvas.before.clear()
        with self.body.canvas.before:
            Color(*color_provider.get_rgba("grey"))
            Rectangle(size=self.body.size, pos=self.body.pos)

    def __update_header(self, *args):
        self.header.canvas.before.clear()
        with self.header.canvas.before:
            Color(*color_provider.get_rgba("blue"))
            Rectangle(size=self.header.size, pos=self.header.pos)

    def __update_footer(self, *args):
        self.footer.canvas.before.clear()
        with self.footer.canvas.before:
            Color(*color_provider.get_rgba("grey"))
            Rectangle(size=self.footer.size, pos=self.footer.pos)
