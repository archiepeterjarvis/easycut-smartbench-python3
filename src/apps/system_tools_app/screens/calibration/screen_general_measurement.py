from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except:
    pass
Builder.load_string(
    """
<GeneralMeasurementScreen>:

    load_graph:load_graph
    plot_title:plot_title

    BoxLayout: 
        orientation: "horizontal"

        BoxLayout: 
            orientation: "vertical"

            Label: 
                id: plot_title
                font_size: str(0.01875 * app.width) + 'sp'

            Image:
                id: load_graph
                size_hint: None, None
                height: dp(0.739583333333*app.height)
                width: dp(0.875*app.width)
                x: dp(5)
                y: dp(5)
                allow_stretch: True
                opacity: 0

        BoxLayout: 
            orientation: "vertical"
            size_hint_x: None
            width: dp(0.125*app.width)
            
            GridLayout: 
                size_hint_y: None
                height: dp(0.208333333333*app.height)
                cols: 2

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "BACK"
                    on_press: root.back_to_fac_settings()

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "Start"
                    on_press: root.start_measurement()

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "Stop"
                    on_press: root.stop_measurement()

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "Clear"
                    on_press: root.clear_measurement()

            GridLayout: 
                cols: 2

                Label:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "y axis"

                Label:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "x axis"

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "t"
                    on_press: root.set_index("X", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "SG X"
                    on_press: root.set_index("Y", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "F"
                    on_press: root.set_index("X", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "SG Y"
                    on_press: root.set_index("Y", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "x pos"
                    on_press: root.set_index("X", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "SG Z"
                    on_press: root.set_index("Y", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "y pos"
                    on_press: root.set_index("X", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "SG Y1"
                    on_press: root.set_index("Y", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "z pos"
                    on_press: root.set_index("X", self)

                Button:
                    font_size: str(0.01875 * app.width) + 'sp'
                    text: "SG Y2"
                    on_press: root.set_index("Y", self)

            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_y: None
                height: dp(0.0833333333333*app.height)
                text: "PLOT"
                on_press: root.display_results()

"""
)


class GeneralMeasurementScreen(Screen):
    x_idx = 0
    y_idx = 0
    descriptors = {
        (1): "x pos",
        (2): "y pos",
        (3): "z pos",
        (4): "SG X",
        (5): "SG Y",
        (6): "SG Y1",
        (7): "SG Y2",
        (8): "SG Z",
        (12): "t",
        (13): "F",
    }

    def __init__(self, machine, systemtools, **kwargs):
        super().__init__(**kwargs)
        self.systemtools_sm = systemtools
        self.m = machine

    def back_to_fac_settings(self):
        self.systemtools_sm.open_factory_settings_screen()

    def start_measurement(self):
        self.m.start_measuring_running_data("999")

    def stop_measurement(self):
        self.m.stop_measuring_running_data()

    def clear_measurement(self):
        self.m.clear_measured_running_data()

    def get_x_axis(self):
        new_list = [i[self.x_idx] for i in self.m.measured_running_data()]
        return new_list

    def get_y_axis(self):
        new_list = [i[self.y_idx] for i in self.m.measured_running_data()]
        return new_list

    def set_index(self, axis, label):
        value = [i for i in self.descriptors if self.descriptors[i] == label.text][0]
        if axis == "X":
            self.x_idx = value
        if axis == "Y":
            self.y_idx = value

    def display_results(self):
        try:
            plt.rcParams["figure.figsize"] = 7, 3.55
            xVar, yVar = zip(
                *(
                    (x, y)
                    for x, y in zip(self.get_x_axis(), self.get_y_axis())
                    if y != -999 and y != None
                )
            )
            plt.plot(xVar, yVar, "bx")
            plt.xlabel(self.descriptors[self.x_idx])
            plt.ylabel(self.descriptors[self.y_idx])
            plt.title(
                self.descriptors[self.x_idx] + "vs" + self.descriptors[self.y_idx]
            )
            plt.tight_layout()
            plt.grid()
            plt.savefig(
                "./asmcnc/apps/systemTools_app/screens/calibration/sg_value_plots.png"
            )
            plt.close()
            self.load_graph.source = (
                "./asmcnc/apps/systemTools_app/screens/calibration/sg_value_plots.png"
            )
            self.load_graph.reload()
            self.load_graph.opacity = 1
            self.plot_title.text = ""
        except:
            self.plot_title.text = "Can't plot :("
