"""
Created Mayh 2019

@author: Letty

Basic screen
"""

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from ui.utils import console_utils

Builder.load_string(
    """

<RebootingScreen>:

    reboot_label: reboot_label

    canvas:
        Color: 
            rgba: hex('#000000')
        Rectangle: 
            size: self.size
            pos: self.pos
             
    BoxLayout:
        orientation: 'horizontal'
        padding:[dp(0.0875)*app.width, dp(0.145833333333)*app.height]
        spacing:0.145833333333*app.height
        size_hint_x: 1

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
                
            Label:
                id: reboot_label
                text_size: self.size
                size_hint_y: 0.5
                markup: True
                font_size: str(0.05*app.width) + 'sp'   
                valign: 'middle'
                halign: 'center'            

"""
)


class RebootingScreen(Screen):
    def __init__(self, localization, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.l = localization
        self.reboot_label.text = self.l.get_str("Rebooting") + "..."

    def on_pre_enter(self):
        self.reboot_label.text = self.l.get_str("Rebooting") + "..."
        self.reboot_label.font_name = self.l.font_regular

    def on_enter(self):
        Clock.schedule_once(console_utils.reboot, 1)
