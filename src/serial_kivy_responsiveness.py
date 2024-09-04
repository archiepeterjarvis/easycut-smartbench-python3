import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from core.serial.serial_conn import SerialConnection
from core.serial.smartbench_controller import SmartBenchController


class StatusLabel(Label):

    def __init__(self, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_text, 0.1)

    i = 0

    def update_text(self, dt):
        self.i += 1
        self.text = f"{self.i}"


class TestStatusBar(BoxLayout):
    orientation = "horizontal"

    def __init__(self, **kwargs):
        super(TestStatusBar, self).__init__(**kwargs)

        self.add_widget(StatusLabel())


class SerialTestApp(App):

    def build(self):
        # self.serial = SerialConnection("/dev/ttyS0")
        # self.controller = SmartBenchController(self.serial)
        # self.serial.open()

        return TestStatusBar()


if __name__ == "__main__":
    SerialTestApp().run()
