"""
Created on 1 Feb 2018
@author: Ed
"""

from kivy.lang import Builder
from kivy.uix.widget import Widget

from ui.components.widgets import widget_z_height
from ui.popups.popups import InfoPopup

Builder.load_string(
    """

<MaintenanceZMove>

    virtual_z_container:virtual_z_container

    BoxLayout:

        size: self.parent.size
        pos: self.parent.pos      
        padding:[dp(0.025)*app.width, dp(0.0416666666667)*app.height]
        spacing:0.025*app.width
        orientation: 'horizontal'
        
        BoxLayout:
            spacing:0.0208333333333*app.height
            orientation: "vertical"
            
            BoxLayout:
                size_hint_y: 3.4
                id: virtual_z_container

        BoxLayout:
            spacing:0.0208333333333*app.height
            orientation: "vertical"
            
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_y: 1
                background_color: hex('#F4433600')
                on_release:
                    root.quit_jog_z()
                    self.background_color = hex('#F4433600')
                on_press:
                    root.jog_z('Z+') 
                    self.background_color = hex('#F44336FF')
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
#                         source: "z_jog_up.png"
                        source: "xy_arrow_up.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True   

            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_y: 1
                background_color: hex('#F4433600')
                on_release: 
                    root.quit_jog_z()
                    self.background_color = hex('#F4433600')
                on_press:
                    root.jog_z('Z-') 
                    self.background_color = hex('#F44336FF')
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "z_jog_down.png"
                        source: "xy_arrow_down.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True   
                        
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                background_color: hex('#F4433600')
                on_press: root.get_info()
                BoxLayout:
                    padding:[dp(0.009375)*app.width, dp(0.0416666666667)*app.height, dp(0.040625)*app.width, dp(0.0416666666667)*app.height]
                    size_hint: (None,None)
                    height: dp(0.208333333333*app.height)
                    width: dp(0.125*app.width)
                    pos: self.parent.pos
                    Image:
                        source: "info_icon.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
        
"""
)


class MaintenanceZMove(Widget):
    def __init__(self, job, localization, screen_manager, machine, **kwargs):
        super().__init__(**kwargs)
        self.m = machine
        self.sm = screen_manager
        self.l = localization
        self.jd = job
        self.virtual_z_container.add_widget(
            widget_z_height.VirtualZ(
                machine=self.m, screen_manager=self.sm, job=self.jd
            )
        )

    def jog_z(self, case):
        self.m.set_led_colour("WHITE")
        feed_speed = self.sm.get_screen("maintenance").xy_move_widget.feedSpeedJogZ
        if self.sm.get_screen("maintenance").xy_move_widget.jogMode == "free":
            if case == "Z-":
                self.m.jog_absolute_single_axis(
                    "Z", self.m.z_min_jog_abs_limit, feed_speed
                )
            if case == "Z+":
                self.m.jog_absolute_single_axis(
                    "Z", self.m.z_max_jog_abs_limit, feed_speed
                )
        elif self.sm.get_screen("maintenance").xy_move_widget.jogMode == "plus_0-01":
            if case == "Z+":
                self.m.jog_relative("Z", 0.01, feed_speed)
            if case == "Z-":
                self.m.jog_relative("Z", -0.01, feed_speed)
        elif self.sm.get_screen("maintenance").xy_move_widget.jogMode == "plus_0-1":
            if case == "Z+":
                self.m.jog_relative("Z", 0.1, feed_speed)
            if case == "Z-":
                self.m.jog_relative("Z", -0.1, feed_speed)
        elif self.sm.get_screen("maintenance").xy_move_widget.jogMode == "plus_1":
            if case == "Z+":
                self.m.jog_relative("Z", 1, feed_speed)
            if case == "Z-":
                self.m.jog_relative("Z", -1, feed_speed)
        elif self.sm.get_screen("maintenance").xy_move_widget.jogMode == "plus_10":
            if case == "Z+":
                self.m.jog_relative("Z", 10, feed_speed)
            if case == "Z-":
                self.m.jog_relative("Z", -10, feed_speed)
        elif self.sm.get_screen("maintenance").xy_move_widget.jogMode == "job":
            if case == "Z-":
                self.m.jog_absolute_single_axis(
                    "Z", self.m.z_min_jog_abs_limit, feed_speed
                )
            if case == "Z+":
                self.m.jog_absolute_single_axis(
                    "Z", self.m.z_max_jog_abs_limit, feed_speed
                )

    def quit_jog_z(self):
        if self.sm.get_screen("maintenance").xy_move_widget.jogMode == "free":
            self.m.quit_jog()
        elif self.sm.get_screen("maintenance").xy_move_widget.jogMode == "job":
            self.m.quit_jog()

    def get_info(self):
        info = (
            self.l.get_bold("To set, if laser hardware is fitted:")
            + "\n\n"
            + self.l.get_str("1. Secure a scrap piece of material to your machine.")
            + "\n"
            + self.l.get_str("2. Enable laser crosshair (switch to on).").replace(
                self.l.get_str("on"), self.l.get_bold("on")
            )
            + "\n"
            + self.l.get_str(
                "3. Move the Z axis down so that it is around 5mm away from the material."
            ).replace(self.l.get_str("5mm"), self.l.get_bold("5mm"))
            + "\n"
            + self.l.get_str("4. Ensure the dust shoe plug is fitted.").replace(
                self.l.get_str("dust shoe plug is fitted"),
                self.l.get_bold("dust shoe plug is fitted"),
            )
            + "\n"
            + self.l.get_str(
                "5. Turn on the spindle, and move the Z axis down in 1mm increments."
            ).replace(self.l.get_str("1mm"), self.l.get_bold("1mm"))
            + "\n"
            + self.l.get_str("6. Make a mark on your scrap material.")
            + "\n"
            + self.l.get_str(
                "7. Lift Z Head and press the reset button in the bottom left."
            ).replace(self.l.get_str("reset"), self.l.get_bold("reset"))
            + "\n"
            + self.l.get_str(
                "8. Move the Z Head so that the cross hair lines up with the mark centre."
            )
            + "\n"
            + self.l.get_str("9. Press save.").replace(
                self.l.get_str("save"), self.l.get_bold("save")
            )
        )
        popup = InfoPopup(
            sm=self.sm,
            m=self.m,
            l=self.l,
            main_string=info,
            popup_width=700,
            popup_height=440,
        )
        popup.open()
