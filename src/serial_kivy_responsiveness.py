from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class StatusLabel(Label):
    def __init__(self, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)
        # self.serial_conn = SerialConnection("/dev/ttyS0")
        # self.serial_conn.open()
        # self.sb_controller = SmartBenchController(self.serial_conn)
        self.i = 0

        # self.serial_conn.bind(last_status=self.update_label)
        Clock.schedule_interval(self.update_label, 0.05)

    def update_label(self, dt):
        self.text = "%s %s" % (dt, self.i)
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
