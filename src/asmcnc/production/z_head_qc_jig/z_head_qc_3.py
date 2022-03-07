from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock

import datetime

Builder.load_string("""
<ZHeadQC3>:
    calibrate_time:calibrate_time

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
                text: 'Countdown to calibration...'
                font_size: dp(50)
            
            Label:
                id: calibrate_time
                text: '00:30:00'
                font_size: dp(50)

""")

class ZHeadQC3(Screen):
    def __init__(self, **kwargs):
        super(ZHeadQC3, self).__init__(**kwargs)

        self.sm = kwargs['sm']
        self.m = kwargs['m']

    def update_time(self, time_left):
        seconds = time_left

        def count_down(seconds):
            if seconds == 0:
                if self.sm.current == self.name:
                    self.sm.current = 'qc4'
                    return
            
            if seconds > 0:
                seconds -= 1
                self.seconds = seconds

            self.calibrate_time.text = str(datetime.timedelta(seconds=seconds))

            Clock.schedule_once(lambda dt: count_down(seconds), 1)

        Clock.schedule_once(lambda dt: count_down(seconds), 0)

    def on_enter(self):
        if self.seconds < 1:
            self.sm.current = 'qc4'

    def enter_prev_screen(self):
        self.sm.current = 'qc2'