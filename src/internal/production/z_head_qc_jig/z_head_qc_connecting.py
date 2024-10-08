import sys
from core.logging.logging_system import Logger
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_string(
    """
<ZHeadQCConnecting>:


    connecting_label: connecting_label

    canvas:
        Color: 
            rgba: hex('#000000')
        Rectangle: 
            size: self.size
            pos: self.pos
             
    BoxLayout:
        orientation: 'horizontal'
        padding: 70
        spacing: 70
        size_hint_x: 1

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
                
            Label:
                id: connecting_label
                text_size: self.size
                size_hint_y: 0.5
                markup: True
                font_size: '40sp'   
                valign: 'middle'
                halign: 'center'    
    

"""
)


class ZHeadQCConnecting(Screen):
    def __init__(self, usb, m, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        self.m = m
        self.usb = usb
        self.connecting_label.text = "Connecting to Z Head..."
        self.z_current = 25
        self.x_current = 26

    def on_enter(self):
        self.connecting_label.text = "Connecting to Z Head..."
        self.ensure_hw_version_and_registers_are_loaded_in()
        if sys.platform == "win32" or sys.platform == "darwin":
            self.progress_to_next_screen()

    def ensure_hw_version_and_registers_are_loaded_in(self):
        if not self.m.s.fw_version:
            Logger.debug("Waiting to get FW version")
            self.connecting_label.text = "Waiting to get FW version"
            Clock.schedule_once(
                lambda dt: self.ensure_hw_version_and_registers_are_loaded_in(), 0.5
            )
            return
        if (
            not self.m.TMC_registers_have_been_read_in()
            and self.m.s.fw_version.startswith("2")
        ):
            Logger.debug("Waiting to get TMC registers")
            self.connecting_label.text = "Waiting to get TMC registers"
            Clock.schedule_once(
                lambda dt: self.ensure_hw_version_and_registers_are_loaded_in(), 1
            )
            return
        if not self.usb.is_available():
            Logger.debug("Getting USB")
            self.connecting_label.text = "Getting USB"
            Clock.schedule_once(
                lambda dt: self.ensure_hw_version_and_registers_are_loaded_in(), 1
            )
            return
        self.progress_to_next_screen()

    def progress_to_next_screen(self):
        Logger.debug("Progress to next screen")
        self.sm.current = "qcpcbsetup"
