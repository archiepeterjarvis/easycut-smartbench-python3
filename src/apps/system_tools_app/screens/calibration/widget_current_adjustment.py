from core.logging.logging_system import Logger
from kivy.lang import Builder
from kivy.uix.widget import Widget
from ui.popups import popup_info

Builder.load_string(
    """
<CurrentAdjustmentWidget>

    motor_label:motor_label
    current_current_label:current_current_label

    BoxLayout:
        size: self.parent.size
        pos: self.parent.pos      
        
        orientation: "vertical"
        
        Button:
            on_press: root.current_up()
            background_color: 1, 1, 1, 0 
            BoxLayout:
                padding: 2
                size: self.parent.size
                pos: self.parent.pos      
                Image:
                    id: speed_image
                    source: "feed_speed_up.png"
                    center_x: self.parent.center_x
                    y: self.parent.y
                    size: self.parent.width, self.parent.height
                    allow_stretch: True  
        Label:
            id: motor_label      

        TextInput:
            id: current_current_label
            markup: True
            font_size: "30sp"
            on_text_validate: root.set_current(self.text)
            input_filter: 'int'
            multiline: False
        
        Button:
            on_press: root.current_down()
            background_color: 1, 1, 1, 0 
            BoxLayout:
                padding: 2
                size: self.parent.size
                pos: self.parent.pos      
                Image:
                    id: speed_image
                    source: "feed_speed_down.png"
                    center_x: self.parent.center_x
                    y: self.parent.y
                    size: self.parent.width, self.parent.height
                    allow_stretch: True

"""
)


class CurrentAdjustmentWidget(Widget):
    def __init__(self, systemtools, localization, motor, m, **kwargs):
        super().__init__(**kwargs)
        self.m = m
        self.motor = motor
        self.l = localization
        self.systemtools_sm = systemtools
        self.motor_name_dict = {
            TMC_X1: "X1",
            TMC_X2: "X2",
            TMC_Y1: "Y1",
            TMC_Y2: "Y2",
            TMC_Z: "Z",
        }
        self.current_current = self.m.TMC_motor[self.motor].ActiveCurrentScale
        self.motor_label.text = self.motor_name_dict[self.motor]
        self.current_current_label.text = str(self.current_current)
        self.current_current_label.bind(focus=self.on_focus)

    def current_up(self):
        self.set_current(self.current_current + 1)

    def current_down(self):
        self.set_current(self.current_current - 1)

    def reset_current(self):
        if self.m.set_motor_current(
            self.motor_name_dict[self.motor],
            self.m.TMC_motor[self.motor].ActiveCurrentScale,
        ):
            self.current_current = self.m.TMC_motor[self.motor].ActiveCurrentScale
            self.current_current_label.text = str(self.current_current)
            return True
        return False

    def on_focus(self, instance, value):
        if not value:
            self.set_current(instance.text)

    def set_current(self, current):
        try:
            if self.m.state().startswith("Idle"):
                if 0 <= int(current) <= 31:
                    self.current_current = int(current)
                    self.m.set_motor_current(
                        self.motor_name_dict[self.motor], self.current_current
                    )
                else:
                    popup_info.PopupError(
                        self.systemtools_sm, self.l, "Invalid current value!"
                    )
            else:
                popup_info.PopupError(
                    self.systemtools_sm, self.l, "Can't change current when not Idle!"
                )
        except:
            popup_info.PopupError(self.systemtools_sm, self.l, "Issue setting current")
            Logger.exception("Error when setting current")
        self.current_current_label.text = str(self.current_current)
        self.current_current_label.focus = False
