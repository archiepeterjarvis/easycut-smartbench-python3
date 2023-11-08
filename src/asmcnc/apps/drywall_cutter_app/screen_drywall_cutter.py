from datetime import datetime

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from asmcnc.skavaUI import popup_info
from asmcnc.apps.drywall_cutter_app import widget_xy_move_drywall
from asmcnc.apps.drywall_cutter_app import widget_drywall_shape_display
from asmcnc.apps.drywall_cutter_app.config import config_loader
from asmcnc.apps.drywall_cutter_app import screen_config_filechooser

Builder.load_string("""
<DrywallCutterScreen>:
    xy_move_container:xy_move_container
    shape_display_container:shape_display_container
    shape_selection:shape_selection
    cut_offset_selection:cut_offset_selection
    rotate_button:rotate_button
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            padding: dp(5)
            spacing: dp(10)
            Button:
                size_hint_x: 7
                text: 'Home'
                on_press: root.home()
            Button:
                size_hint_x: 7
                text: 'File'
                on_press: root.open_filechooser()
            Spinner:
                size_hint_x: 7
                text: 'Tool'
                values: root.tool_options
            Spinner:
                id: shape_selection
                size_hint_x: 7
                text: 'Shape'
                values: root.shape_options
                on_text: root.select_shape()
            Button:
                id: rotate_button
                size_hint_x: 7
                text: 'Rotate'
                on_press: root.rotate_shape()
            Spinner:
                id: cut_offset_selection
                size_hint_x: 7
                text: 'Cut on line'
                text_size: self.size
                halign: 'center'
                valign: 'middle'
                values: root.line_cut_options
                on_text: root.select_toolpath()
            Button:
                size_hint_x: 7
                text: 'Material setup'
                text_size: self.size
                halign: 'center'
                valign: 'middle'
                on_press: root.material_setup()
            Button:
                size_hint_x: 15
                text: 'STOP'
                on_press: root.stop()
            Button:
                size_hint_x: 7
                on_press: root.quit_to_lobby()
                text: 'Quit'
        BoxLayout:
            size_hint_y: 5
            orientation: 'horizontal'
            padding: dp(5)
            spacing: dp(10)
            BoxLayout:
                id: shape_display_container
                size_hint_x: 55
            BoxLayout:
                size_hint_x: 23
                orientation: 'vertical'
                spacing: dp(10)
                BoxLayout:
                    id: xy_move_container
                    size_hint_y: 31
                    padding: [dp(0), dp(30)]
                    canvas.before:
                        Color:
                            rgba: hex('#E5E5E5FF')
                        Rectangle:
                            size: self.size
                            pos: self.pos
                BoxLayout:
                    size_hint_y: 7
                    orientation: 'horizontal'
                    spacing: dp(10)
                    Button:
                        text: 'Simulate'
                        on_press: root.simulate()
                    Button:
                        text: 'Save'
                        on_press: root.save()
                    Button:
                        text: 'Run'
                        on_press: root.run()
""")


def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f')[:12] + ' ' + message)


class DrywallCutterScreen(Screen):
    tool_options = ['6mm', '8mm', 'V groove']
    shape_options = ['circle', 'square', 'rectangle', 'line', 'geberit']
    line_cut_options = ['inside', 'on', 'outside']
    rotation = 'horizontal'
    dwt_config = config_loader.DWTConfig()

    def __init__(self, **kwargs):
        super(DrywallCutterScreen, self).__init__(**kwargs)

        self.sm = kwargs['screen_manager']
        self.m = kwargs['machine']
        self.l = kwargs['localization']

        # XY move widget
        self.xy_move_widget = widget_xy_move_drywall.XYMoveDrywall(machine=self.m, screen_manager=self.sm)
        self.xy_move_container.add_widget(self.xy_move_widget)

        self.drywall_shape_display_widget = widget_drywall_shape_display.DrywallShapeDisplay(machine=self.m, screen_manager=self.sm, dwt_config=self.dwt_config)
        self.shape_display_container.add_widget(self.drywall_shape_display_widget)

        self.shape_selection.text = 'circle'

    def home(self):
        self.m.request_homing_procedure('drywall_cutter', 'drywall_cutter')

    def select_shape(self):
        if self.shape_selection.text in ['line', 'geberit']:
            # Only on line available for these options
            self.cut_offset_selection.text = 'on'
            self.cut_offset_selection.disabled = True
        else:
            # Default to cut inside line
            self.cut_offset_selection.text = 'inside'
            self.cut_offset_selection.disabled = False

        if self.shape_selection.text in ['rectangle', 'line']:
            self.rotate_button.disabled = False
        else:
            self.rotate_button.disabled = True

        self.rotation = 'horizontal'
        self.drywall_shape_display_widget.select_shape(self.shape_selection.text, self.rotation)
        self.select_toolpath()

        self.dwt_config.on_parameter_change('shape_type', self.shape_selection.text)

    def rotate_shape(self, swap_lengths=True):
        if self.rotation == 'horizontal':
            self.rotation = 'vertical'
        else:
            self.rotation = 'horizontal'
        self.drywall_shape_display_widget.select_shape(self.shape_selection.text, self.rotation, swap_lengths=swap_lengths)
        self.select_toolpath()

    def select_toolpath(self):
        self.drywall_shape_display_widget.select_toolpath(self.shape_selection.text, self.cut_offset_selection.text, self.rotation)

        self.dwt_config.on_parameter_change('toolpath_offset', self.cut_offset_selection.text)

    def material_setup(self):
        pass

    def stop(self):
        popup_info.PopupStop(self.m, self.sm, self.l)

    def quit_to_lobby(self):
        self.sm.current = 'lobby'

    def simulate(self):
        pass

    def save(self):
        pass

    def run(self):
        pass

    def open_filechooser(self):
        if not self.sm.has_screen('config_filechooser'):
            self.sm.add_widget(screen_config_filechooser.ConfigFileChooser(name='config_filechooser',
                                                                           screen_manager=self.sm,
                                                                           localization=self.l,
                                                                           callback=self.load_config))
        self.sm.current = 'config_filechooser'

    def load_config(self, config):
        # type: (str) -> None
        """
        Used as the callback for the config filechooser screen.

        :param config: The path to the config file, including extension.
        """
        self.dwt_config.load_config(config)

        file_name_no_ext = config.split('/')[-1].split('.')[0]

        # set the label on the screen to the name of the config file below

        toolpath_offset = self.dwt_config.active_config.toolpath_offset
        self.shape_selection.text = self.dwt_config.active_config.shape_type
        self.select_shape()

        self.cut_offset_selection.text = toolpath_offset
        self.select_toolpath()

        self.drywall_shape_display_widget.d_input.text = str(self.dwt_config.active_config.canvas_shape_dims.d)
        self.drywall_shape_display_widget.l_input.text = str(self.dwt_config.active_config.canvas_shape_dims.l)
        self.drywall_shape_display_widget.r_input.text = str(self.dwt_config.active_config.canvas_shape_dims.r)
        self.drywall_shape_display_widget.x_input.text = str(self.dwt_config.active_config.canvas_shape_dims.x)
        self.drywall_shape_display_widget.y_input.text = str(self.dwt_config.active_config.canvas_shape_dims.y)

    def on_leave(self, *args):
        self.dwt_config.save_temp_config()
