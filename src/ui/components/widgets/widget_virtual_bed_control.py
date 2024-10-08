"""
Created on 1 Feb 2018
@author: Ed
"""

import textwrap
from kivy.lang import Builder
from kivy.uix.widget import Widget
from ui.popups import popup_info

Builder.load_string(
    """

#:import hex kivy.utils.get_color_from_hex

<VirtualBedControl>

    BoxLayout:
        size: self.parent.size
        pos: self.parent.pos   
        padding: 0
        spacing: 20
        orientation: "horizontal"

        BoxLayout:
            size_hint_x: 2 
            size: self.parent.size
            pos: self.parent.pos   
            padding: 5
            spacing: 5
            orientation: "horizontal"
            canvas:
                Color: 
                    rgba: hex('FFFFFFFF')
                RoundedRectangle: 
                    size: self.size
                    pos: self.pos

            Label:
                text: 'SET:'
                size_hint_x: 1 
                markup: True
                color: hex('#ff9800ff')
                font_size: 20.0 / 800 * app.width

            Button:
                background_color: hex('#F4433600')
                on_release: 
                    self.background_color = hex('#F4433600')
                on_press: 
                    root.set_standby_to_pos()
                    self.background_color = hex('#F44336FF')
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "park.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
    
            Button:
                background_color: hex('#F4433600')
                on_release: 
                    self.background_color = hex('#F4433600')
                on_press: 
                    root.set_workzone_to_pos_xy()
                    self.background_color = hex('#F44336FF')
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "jobstart.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True       
        
        
        BoxLayout:
            size_hint_x: 2 
            size: self.parent.size
            pos: self.parent.pos   
#             padding: 5
#             spacing: 5
#             orientation: "horizontal"
#             canvas:
#                 Color: 
#                     rgba: hex('FFFFFFFF')
#                 RoundedRectangle: 
#                     size: self.size
#                     pos: self.pos


        BoxLayout:
            size_hint_x: 2 
            size: self.parent.size
            pos: self.parent.pos   
            padding: 5
            spacing: 5
            orientation: "horizontal"
            canvas:
                Color: 
                    rgba: hex('FFFFFFFF')
                RoundedRectangle: 
                    size: self.size
                    pos: self.pos
            Label:
                text: ' GO:'
                size_hint_x: 1 
                markup: True
                color: hex('#4caf50ff')
                font_size: 20.0 / 800 * app.width    
            Button:
                background_color: hex('#F4433600')
                on_release: 
                    self.background_color = hex('#F4433600')
                on_press: 
                    root.go_to_standby()
                    self.background_color = hex('#F44336FF')
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "park.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                      
            Button:
                background_color: hex('#F4433600')
                on_release: 
                    self.background_color = hex('#F4433600')
                on_press: 
                    root.go_to_jobstart_xy()
                    self.background_color = hex('#F44336FF')
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "jobstart.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
    
    
     
"""
)


class VirtualBedControl(Widget):
    def __init__(self, localization, screen_manager, machine, **kwargs):
        super().__init__(**kwargs)
        self.m = machine
        self.sm = screen_manager
        self.l = localization

    def zoomStateCheck(self):
        if self.zoomToggleButton.state == "down":
            self.bedWidgetScatter.do_translation = True
            self.bedWidgetScatter.do_scale = True
        if self.zoomToggleButton.state == "normal":
            self.bedWidgetScatter.do_translation = False
            self.bedWidgetScatter.do_scale = False

    def set_workzone_to_pos_xy(self):
        warning = self.format_command(
            self.l.get_str("Is this where you want to set your X-Y datum?")
            .replace("X-Y", "[b]X-Y[/b]")
            .replace(self.l.get_str("datum"), self.l.get_bold("datum"))
        )
        popup_info.PopupDatum(self.sm, self.m, self.l, "XY", warning)

    def set_standby_to_pos(self):
        warning = self.format_command(
            self.l.get_str("Is this where you want to set your standby position?")
        )
        popup_info.PopupPark(self.sm, self.m, self.l, warning)

    def go_to_jobstart_xy(self):
        if self.m.is_machine_homed == False:
            popup_info.PopupHomingWarning(self.sm, self.m, self.l, "home", "home")
        else:
            self.m.go_to_jobstart_xy()

    def go_to_standby(self):
        if self.m.is_machine_homed == False:
            popup_info.PopupHomingWarning(self.sm, self.m, self.l, "home", "home")
        else:
            self.m.go_to_standby()

    def format_command(self, cmd):
        wrapped_cmd = textwrap.fill(cmd, width=35, break_long_words=False)
        return wrapped_cmd
