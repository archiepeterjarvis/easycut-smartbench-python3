"""
Created on 1 Feb 2018
@author: Ed
"""

from kivy.lang import Builder
from kivy.uix.widget import Widget

from ui.components.buttons.spindle_button import SpindleButton
from ui.components.buttons.vacuum_button import VacuumButton
from ui.utils import scaling_utils

Builder.load_string(
    """
<CommonMove>

    speed_image:speed_image
    speed_toggle:speed_toggle
    vacuum_spindle_container:vacuum_spindle_container
    spindle_container:spindle_container
    vacuum_container:vacuum_container

    BoxLayout:
        size: self.parent.size
        pos: self.parent.pos      

        spacing:0.0416666666667*app.height
        
        orientation: "vertical"
        
        BoxLayout:
            spacing: 0
            padding:dp(0)
            size_hint_y: 1
            orientation: 'vertical'
            canvas:
                Color: 
                    rgba: 1,1,1,1
                RoundedRectangle: 
                    size: self.size
                    pos: self.pos 

            ToggleButton:
                font_size: str(0.01875 * app.width) + 'sp'
                id: speed_toggle
                on_press: root.set_jog_speeds()
                background_color: 1, 1, 1, 0 
                BoxLayout:
                    padding:[dp(0.0125)*app.width, dp(0.0208333333333)*app.height]
                    size: self.parent.size
                    pos: self.parent.pos      
                    Image:
                        id: speed_image
                        source: "slow.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True  
            
        BoxLayout:
            spacing: 0
            padding:dp(0)
            size_hint_y: 2
            orientation: 'vertical'
            id: vacuum_spindle_container
            canvas:
                Color: 
                    rgba: 1,1,1,1
                RoundedRectangle: 
                    size: self.size
                    pos: self.pos 

            BoxLayout:
                id: vacuum_container
                size_hint_y: 1
                padding: [dp(app.get_scaled_width(10)), dp(app.get_scaled_height(10))]
            
            BoxLayout:
                id: spindle_container
                size_hint_y: 1
                padding: [dp(app.get_scaled_width(10)), dp(app.get_scaled_height(10))]
"""
)


class CommonMove(Widget):
    def __init__(self, screen_manager, machine, **kwargs):
        super().__init__(**kwargs)
        self.m = machine
        self.sm = screen_manager
        self.set_jog_speeds()
        self.add_buttons()

    spindle_button = None
    vacuum_button = None

    def add_buttons(self):
        self.vacuum_button = VacuumButton(
            self.m,
            self.m.s,
            size_hint=(None, None),
            size=(
                scaling_utils.get_scaled_dp_width(71),
                scaling_utils.get_scaled_dp_height(72),
            ),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.vacuum_container.add_widget(self.vacuum_button)
        self.spindle_button = SpindleButton(
            self.m,
            self.m.s,
            self.sm,
            size_hint=(None, None),
            size=(
                scaling_utils.get_scaled_dp_width(71),
                scaling_utils.get_scaled_dp_height(72),
            ),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.spindle_container.add_widget(self.spindle_button)

    fast_x_speed = 6000
    fast_y_speed = 6000
    fast_z_speed = 750

    def set_jog_speeds(self):
        if self.speed_toggle.state == "normal":
            self.speed_image.source = "slow.png"
            self.feedSpeedJogX = self.fast_x_speed / 5
            self.feedSpeedJogY = self.fast_y_speed / 5
            self.feedSpeedJogZ = self.fast_z_speed / 5
        else:
            self.speed_image.source = "fast.png"
            self.feedSpeedJogX = self.fast_x_speed
            self.feedSpeedJogY = self.fast_y_speed
            self.feedSpeedJogZ = self.fast_z_speed
