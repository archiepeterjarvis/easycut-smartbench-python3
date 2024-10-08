from kivy.lang import Builder
from kivy.uix.widget import Widget

Builder.load_string(
    """

<NudgeSpeed>

    speed_toggle:speed_toggle
    speed_image:speed_image

    BoxLayout:
        size: self.parent.size
        pos: self.parent.pos
        orientation: 'vertical'
        spacing: 10
        padding: 10

        ToggleButton:
            id: speed_toggle
            on_press: root.set_jog_speeds()
            background_color: 1, 1, 1, 0
            BoxLayout:
                size: self.parent.size
                pos: self.parent.pos
                Image:
                    id: speed_image
                    source: "slow.png"
                    center_x: self.parent.center_x
                    y: self.parent.y
                    size: self.parent.width, self.parent.height
                    allow_stretch: True

        Button:
            background_color: hex('#F4433600')
            on_release: 
                self.background_color = hex('#F4433600')
            on_press: 
                root.set_datum()
                self.background_color = hex('#F44336FF')
            BoxLayout:
                padding: 5
                size: self.parent.size
                pos: self.parent.pos      
                Image:
                    source: "set_jobstart.png"
                    center_x: self.parent.center_x
                    y: self.parent.y
                    size: self.parent.width, self.parent.height
                    allow_stretch: True

"""
)


class NudgeSpeed(Widget):
    def __init__(self, screen_manager, machine, **kwargs):
        super().__init__(**kwargs)
        self.m = machine
        self.sm = screen_manager
        self.set_jog_speeds()

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

    def set_datum(self):
        self.sm.get_screen("nudge").set_datum_popup()
