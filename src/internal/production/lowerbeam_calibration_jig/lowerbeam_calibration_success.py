from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

Builder.load_string(
    """
<LBCalibrationSuccess>:
    success_label:success_label

    canvas:
        Color:
            rgba: hex('#4CAF50FF')
        Rectangle:
            pos:self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 1.00

        Button:
            text: '<<< Back'
            on_press: root.enter_prev_screen()
            text_size: self.size
            markup: 'True'
            halign: 'left'
            valign: 'middle'
            padding: [dp(10),0]
            size_hint_y: 0.2
            size_hint_x: 0.5
            font_size: dp(20)

        GridLayout:
            cols: 1
            rows: 2

            Label:
                id: success_label
                text: 'Database updated for '
                font_size: dp(50)
            
            Button:
                on_press: console_utils.shutdown()
                text: 'OK, SHUT DOWN'
                font_size: dp(30)
                size_hint_y: 0.2
                size_hint_x: 0.3

"""
)


class LBCalibrationSuccess(Screen):
    def __init__(self, m, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        self.m = m

    def enter_prev_screen(self):
        self.sm.current = "lbc4"

    def set_serial_no(self, serial_no):
        self.success_label.text = "Database updated for: " + serial_no
