from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from core.serial.serial_conn import SerialConnection
from core.serial.smartbench_controller import SmartBenchController


class StatusLabel(Label):

    def __init__(self, controller, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)
        self.controller = controller
        self.controller.serial_conn.bind(last_status=self.update_text)

    i = 0
    def update_text(self, instance, value):
        self.i += 1
        self.text = f"{value}: {self.i}"


class TestStatusBar(BoxLayout):
    orientation = "horizontal"

    def __init__(self, controller, **kwargs):
        super(TestStatusBar, self).__init__(**kwargs)

        self.add_widget(StatusLabel(controller))


class SerialTestApp(App):

    def build(self):
        self.serial = SerialConnection(SerialConnection.get_available_ports()[0].device)
        self.serial.open()
        self.controller = SmartBenchController(self.serial)

        return TestStatusBar(self.controller)


if __name__ == "__main__":
    SerialTestApp().run()
