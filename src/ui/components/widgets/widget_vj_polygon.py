from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty
from kivy.clock import Clock
from core.logging.logging_system import Logger
from core.job.geometry import geometry
from asmcnc.gcode_writer import GcodeWriter

Builder.load_string(
    """

#:import hex kivy.utils.get_color_from_hex

<PolygonVJ>:

    sides_textinput2 : sides_textinput
    rad_textinput2 : rad_textinput

    BoxLayout:
        padding: 20
        spacing: 20
        size: root.size
        pos: root.pos
        orientation: "vertical"
        
        BoxLayout:
            size_hint_y: 1
            orientation: 'horizontal'
            size: self.parent.size
            pos: self.parent.pos
            padding: 15

            canvas.before:
                Color: 
                    rgba: 1,1,1,1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos

            Label:
                text: 'Bit dia:'
                size_hint_x:1
                font_size:20
                color: 0,0,0,.8
            TextInput:
                id: bit_dia_textinput
                size_hint_x: 1
                font_size:24
                multiline: False

            Label:
                text: 'Depth:'
                size_hint_x: 1
                font_size:20
                color: 0,0,0,.8
            TextInput:
                id: depth_textinput
                size_hint_x: 1
                font_size:24
                multiline: False

            Label:
                #id: sides_textinput_
                text: 'Sides:'
                size_hint_x: 1
                font_size:20
                color: 0,0,0,.8
            TextInput:
                id: sides_textinput
                text: "3"
                size_hint_x: 1
                font_size:24
                multiline: False
                on_touch_up: self.select_all()
                on_text: root.on_sides_textinput()

            Label:
                text: 'Rad:'
                size_hint_x: 1
                font_size:20
                color: 0,0,0,.8
            TextInput:
                id: rad_textinput
                text: "80"
                size_hint_x: 1
                font_size:24
                multiline: False
                on_touch_up: self.select_all()
                on_text: root.on_sides_textinput()

#             Label:
#                 text: 'B:'
#                 size_hint_x: 1
#                 font_size:20
#                 color: 0,0,0,.8
#             TextInput:
#                 id: b_textinput
#                 size_hint_x: 1
#                 font_size:24
#                 multiline: False
        
        BoxLayout:
            size_hint_y: 5
            orientation: 'horizontal'
            size: self.parent.size
            pos: self.parent.pos
            padding: 0
            spacing: 20
            
            BoxLayout:
                size_hint_x: 6
                size: self.parent.size
                pos: self.parent.pos
                padding: 20

                canvas:
                    Color: 
                        rgba: 1,1,1,1
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgba: 1,0.5,1,1
                    Line:
                        points: root.points
                        close: True
                        width: 5

            StackLayout:
                #size_hint_x: 1
                orientation: 'bt-lr'
                spacing: 10

                canvas:
                    Color: 
                        rgba: 1,1,1,1
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos

                Button:
                    id: ok
#                    text: 'OK'
                    disabled: False
                    size_hint_y: 0.25
                    #size: [50,50]
                    background_color: hex('#FFFFFF00')
                    on_release:
                        self.background_color = hex('#FFFFFF00')
                    on_press:
                        self.background_color = hex('#FFFFFFFF')
                        root.on_ok()
                    BoxLayout:
                        padding: 20
                        size: self.parent.size
                        pos: self.parent.pos
                        Image:
                            id: image_select
                            source: "file_select_select.png"
                            #center_x: self.parent.center_x
                            #y: self.parent.y
                            #size: self.parent.width, self.parent.height
                            #allow_stretch: True

                Button:
                    id: cancel
#                    text: 'Cancel'
                    disabled: False
                    size_hint_y:0.25
                    #size: [50,50]
                    background_color: hex('#FFFFFF00')
                    on_release:
#                        root.manager.current = 'lobby'
                        self.background_color = hex('#FFFFFF00')
                    on_press:
                        root.sm.current = 'lobby'
                        self.background_color = hex('#FFFFFFFF')
                    BoxLayout:
                        padding: 20
                        size: self.parent.size
                        pos: self.parent.pos
                        Image:
                            id: image_cancel
                            source: "template_cancel.png"
                            #center_x: self.parent.center_x
                            #y: self.parent.y
                            #size: self.parent.width, self.parent.height
                            #allow_stretch: True 

                Button:
                    id: left_button
                    disabled: False
                    size_hint_y: 0.25
                    background_color: hex('#FFFFFF00')
                    on_release:
#                        carousel.load_previous()
#                        root.manager.current = 'template'
                        self.background_color = hex('#FFFFFF00')
                    on_press:
                        root.sm.current = 'template'
                        self.background_color = hex('#FFFFFFFF')
                    BoxLayout:
                        padding: 10
                        size: self.parent.size
                        pos: self.parent.pos
                        Image:
                            id: image_select
                            source: "xy_arrow_left.png"
                            center_x: self.parent.center_x
                            y: self.parent.y
                            size: self.parent.width, self.parent.height
                            allow_stretch: True

                Button:
                    id: right_button
                    disabled: False
                    size_hint_y: 0.25
                    background_color: hex('#FFFFFF00')
                    on_release:
#                        carousel.load_next(mode='next')
                        self.background_color = hex('#FFFFFF00')
                    on_press:
                        root.sm.current = 'template'
                        self.background_color = hex('#FFFFFFFF')
                    BoxLayout:
                        padding: 10
                        size: self.parent.size
                        pos: self.parent.pos
                        Image:
                            id: image_cancel
                            source: "xy_arrow_right.png"
                            center_x: self.parent.center_x
                            y: self.parent.y
                            size: self.parent.width, self.parent.height
                            allow_stretch: True 
"""
)


class PolygonVJ(Widget):
    sm = None
    sides_textinput2 = ObjectProperty()
    rad_textinput2 = ObjectProperty()
    points = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.my_callback, 0)

    def my_callback(self, dt):
        polygon_vertices = geometry.compute_polygon_points(
            float(self.sides_textinput2.text), float(self.rad_textinput2.text)
        )
        self.plot_ploygon(polygon_vertices)

    def on_sides_textinput(self):
        if self.sides_textinput2.text and float(self.sides_textinput2.text) > 2:
            Logger.debug("on_sides_textinput " + str(self.sides_textinput2.text))
            polygon_vertices = geometry.compute_polygon_points(
                float(self.sides_textinput2.text), float(self.rad_textinput2.text)
            )
            self.plot_ploygon(polygon_vertices)

    def on_rad_textinput(self):
        if self.rad_textinput2.text and float(self.rad_textinput2.text) > 0:
            Logger.debug("on_rad_textinput " + str(self.rad_textinput2.text))
            polygon_vertices = geometry.compute_polygon_points(
                float(self.sides_textinput2.text), float(self.rad_textinput2.text)
            )
            self.plot_ploygon(polygon_vertices)

    def on_ok(self):
        Logger.info("on_ok")
        self.generate_gcode()

    def generate_gcode(self):
        my_gcode_writer = GcodeWriter()
        layers_points = []
        layers_points.append(self.points)
        my_gcode_writer.write_gcode(
            "ae_test.nc", layers_points, bit_width=3, depth_increment=0.1, feedrate=1000
        )

    def plot_ploygon(self, polygon_vertices):
        self.points = []
        for point in polygon_vertices:
            self.points.append(point[0])
            self.points.append(point[1])

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            return True
