from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class Dispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        super(Dispatcher, self).__init__(**kwargs)
        self.register_event_type("on_update")

        Clock.schedule_interval(self.dis, 0.05)

    def on_update(self, *args):
        pass

    def dis(self, dt):
        self.dispatch("on_update")


class StatusLabel(Label):
    def __init__(self, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)

        self.dispatcher = Dispatcher()
        self.dispatcher.bind(on_update=self.update_label)

    i = 0

    def update_label(self, dt):
        self.text = f"{self.i}"
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
