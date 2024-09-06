from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from core.serial.serial_conn import SerialConnection
from core.serial.smartbench_controller import SmartBenchController


class StatusLabel(Label):
    def __init__(self, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)
        self.serial_conn = SerialConnection(SerialConnection.get_available_ports()[1].device)
        self.serial_conn.open()
        self.sb_controller = SmartBenchController(self.serial_conn)
        self.i = 0

        self.serial_conn.bind(last_status=self.update_label)

    def update_label(self, instance, value):
        self.text = f"{value} {self.i}"
        self.i += 1


class TestStatusBar(BoxLayout):
    orientation = "horizontal"

    def __init__(self, **kwargs):
        super(TestStatusBar, self).__init__(**kwargs)

        self.add_widget(StatusLabel())


class SerialTestApp(App):
    def build(self):
        return TestStatusBar()


if __name__ == "__main__":
    SerialTestApp().run()
