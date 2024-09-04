"""
Created on 4 March 2020
Screen 25 for the Shape Cutter App

@author: Letty
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from interface.core_UI.popups import WarningPopup

Builder.load_string(
    """

<ShapeCutter25ScreenClass>

    info_button: info_button
    file_name: file_name
    save_image: save_image
    
    on_touch_down: root.on_touch()

    BoxLayout:
        size_hint: (None,None)
        width: dp(1.0*app.width)
        height: dp(1.0*app.height)
        padding: 0
        spacing: 0
        orientation: "vertical"

        BoxLayout:
            size_hint: (None,None)
            width: dp(1.0*app.width)
            height: dp(0.1875*app.height)
            padding: 0
            spacing: 0
            orientation: "horizontal"

            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint: (None,None)
                height: dp(0.1875*app.height)
                width: dp(0.1775*app.width)
                on_press: root.prepare()
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "prepare_tab_blue.png"
                        size: self.parent.size
                        allow_stretch: True
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint: (None,None)
                height: dp(0.1875*app.height)
                width: dp(0.1775*app.width)
                on_press: root.load()
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "load_tab_blue.png"
                        size: self.parent.size
                        allow_stretch: True
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint: (None,None)
                height: dp(0.1875*app.height)
                width: dp(0.1775*app.width)
                on_press: root.define()
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "define_job_tab_grey.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint: (None,None)
                height: dp(0.1875*app.height)
                width: dp(0.1775*app.width)
                on_press: root.position()
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "position_tab_blue.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint: (None,None)
                height: dp(0.1875*app.height)
                width: dp(0.1775*app.width)
                on_press: root.check()
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "check_tab_blue.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint: (None,None)
                height: dp(0.1875*app.height)
                width: dp(0.1125*app.width)
                on_press: root.exit()
                BoxLayout:
                    padding: 0
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "exit_cross.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True                    
                    
        BoxLayout:
            size_hint: (None,None)
            padding: 0
            height: dp(0.8125*app.height)
            width: dp(1.0*app.width)
            canvas:
                Rectangle: 
                    pos: self.pos
                    size: self.size
                    source: "background.png"
            
            BoxLayout:
                orientation: "vertical"
                padding: 0
                spacing: 0
                    
                BoxLayout: #Header
                    size_hint: (None,None)
                    height: dp(0.125*app.height)
                    width: dp(1.0*app.width)
                    padding:[dp(0.025)*app.width, 0, 0, 0]
                    orientation: "horizontal"
                    
                    BoxLayout: #Screen number
                        size_hint: (None,None)
                        padding: 0
                        height: dp(0.0833333333333*app.height)
                        width: dp(0.05*app.width)
                        canvas:
                            Rectangle: 
                                pos: self.pos
                                size: self.size
                                source: "number_box.png"
                        Label:
                            text: root.screen_number
                            valign: "middle"
                            halign: "center"
                            font_size: 0.0325*app.width
                            markup: True
                                
                                
                        
                    BoxLayout: #Title
                        size_hint: (None,None)
                        height: dp(0.125*app.height)
                        width: dp(0.925*app.width)
                        padding:[dp(0.025)*app.width, dp(0.0416666666667)*app.height, 0, 0]
                        
                        Label:
                            text: root.title_label
                            color: 0,0,0,1
                            font_size: 0.035*app.width
                            markup: True
                            halign: "left"
                            valign: "bottom"
                            text_size: self.size
                            size: self.parent.size
                            pos: self.parent.pos
                        
                    
                BoxLayout: #Body
                    size_hint: (None,None)
                    height: dp(0.6875*app.height)
                    width: dp(1.0*app.width)
                    padding:[0, dp(0.0416666666667)*app.height, 0, 0]
                    orientation: "horizontal"
                    
                    BoxLayout: #text box
                        size_hint: (None,None)
                        height: dp(0.645833333333*app.height)
                        width: dp(0.84375*app.width)
                        padding:[dp(0.0125)*app.width, 0, dp(0.03125)*app.width, dp(0.0208333333333)*app.height]
                        orientation: "horizontal"
                        BoxLayout: # file save
                            size_hint: (None,None)
                            height: dp(0.625*app.height)
                            width: dp(0.375*app.width)
                            padding:[0, 0, 0, 0]
                            orientation: "vertical"       
                            BoxLayout: 
                                size_hint: (None,None)
                                height: dp(0.145833333333*app.height)
                                width: dp(0.375*app.width)
                                padding:[0, 0, 0, dp(0.0104166666667)*app.height]
                                orientation: "vertical"

#                                 Label: 
#                                     text: ""
#                                     color: 0,0,0,1
#                                     font_size: 20
#                                     markup: True
#                                     halign: "center"
#                                     valign: "top"
#                                     text_size: self.size
#                                     size: self.parent.size
#                                     pos: self.parent.pos
                                    
                                BoxLayout: 
                                    size_hint: (None,None)
                                    height: dp(0.0833333333333*app.height)
                                    width: dp(0.375*app.width)
                                    padding:[dp(0.0125)*app.width, 0, dp(0.0125)*app.width, 0]
                                                
                                    TextInput: 
                                        id: file_name
                                        valign: 'middle'
                                        halign: 'center'
                                        text_size: self.size
                                        font_size: str(0.025*app.width) + 'sp'
                                        markup: True
                                        multiline: False
                                        text: ''                           
                            BoxLayout: 
                                size_hint: (None,None)
                                height: dp(0.35*app.height)
                                width: dp(0.375*app.width)
                                padding:[dp(0.0825)*app.width, 0, dp(0.0825)*app.width, 0]
                                Button:
                                    font_size: str(0.01875 * app.width) + 'sp'
                                    size_hint: (None,None)
                                    height: dp(0.35*app.height)
                                    width: dp(0.21*app.width)
                                    on_press: root.save_file()
                                    background_color: hex('#F4433600')
                                    BoxLayout:
                                        padding: 0
                                        size: self.parent.size
                                        pos: self.parent.pos
                                        Image:
                                            id: save_image
                                            source: "save_file.png"
                                            size: self.parent.size
                                            allow_stretch: True
                            BoxLayout: 
                                size_hint: (None,None)
                                height: dp(0.129166666667*app.height)
                                width: dp(0.375*app.width)
                                padding:[0, 0, 0, 0]
                                Label: 
                                    text: "You can save this profile later after the job too. "
                                    color: 0,0,0,1
                                    font_size: 0.025*app.width
                                    markup: True
                                    halign: "center"
                                    valign: "middle"
                                    text_size: self.size
                                    size: self.parent.size
                                    pos: self.parent.pos                                            
                                            
                        BoxLayout: # document viewer
                            size_hint: (None,None)
                            height: dp(0.625*app.height)
                            width: dp(0.4375*app.width)
                            padding:[0, 0, 0, 0]
                            ScrollView:
                                size_hint: (None, None)
                                size: self.parent.size
                                pos: self.parent.pos
                                do_scroll_x: True
                                do_scroll_y: True
                                scroll_type: ['content']
                                RstDocument:
                                    text: root.display_profile
                                    background_color: hex('#FFFFFF')
                                    base_font_size: str(31.0/800.0*app.width) + 'sp'

                    BoxLayout: #action box
                        size_hint: (None,None)
                        height: dp(0.645833333333*app.height)
                        width: dp(0.15625*app.width)
                        padding:[0, 0, 0, dp(0.0708333333333)*app.height]
                        spacing:0.0708333333333*app.height
                        orientation: "vertical"
                        
                        BoxLayout: 
                            size_hint: (None,None)
                            height: dp(0.139583333333*app.height)
                            width: dp(0.11*app.width)
                            padding:[dp(0.03)*app.width, 0, dp(0.03)*app.width, dp(0.0708333333333)*app.height]
                            Button:
                                font_size: str(0.01875 * app.width) + 'sp'
                                id: info_button
                                size_hint: (None,None)
                                height: dp(0.0833333333333*app.height)
                                width: dp(0.05*app.width)
                                background_color: hex('#F4433600')
                                opacity: 1
                                on_press: root.get_info()
                                BoxLayout:
                                    padding: 0
                                    size: self.parent.size
                                    pos: self.parent.pos
                                    Image:
                                        source: "info_icon.png"
                                        center_x: self.parent.center_x
                                        y: self.parent.y
                                        size: self.parent.width, self.parent.height
                                        allow_stretch: True

                        Button: 
                            font_size: str(0.01875 * app.width) + 'sp'
                            size_hint: (None,None)
                            height: dp(0.139583333333*app.height)
                            width: dp(0.11*app.width)
                            background_color: hex('#F4433600')
                            on_press: root.go_back()
                            BoxLayout:
                                padding: 0
                                size: self.parent.size
                                pos: self.parent.pos
                                Image:
                                    source: "arrow_back.png"
                                    center_x: self.parent.center_x
                                    y: self.parent.y
                                    size: self.parent.width, self.parent.height
                                    allow_stretch: True
                        Button: 
                            font_size: str(0.01875 * app.width) + 'sp'
                            size_hint: (None,None)
                            height: dp(0.139583333333*app.height)
                            width: dp(0.11*app.width)
                            background_color: hex('#F4433600')
                            on_press: root.next_screen()
                            BoxLayout:
                                padding: 0
                                size: self.parent.size
                                pos: self.parent.pos
                                Image:
                                    source: "arrow_next.png"
                                    center_x: self.parent.center_x
                                    y: self.parent.y
                                    size: self.parent.width, self.parent.height
                                    allow_stretch: True               

"""
)


class ShapeCutter25ScreenClass(Screen):
    info_button = ObjectProperty()
    screen_number = StringProperty("[b]25[/b]")
    title_label = StringProperty("[b]Would you like to save this as a new profile?[/b]")
    display_profile = StringProperty()

    def __init__(self, keyboard, job_parameters, machine, shapecutter, **kwargs):
        super().__init__(**kwargs)
        self.shapecutter_sm = shapecutter
        self.m = machine
        self.j = job_parameters
        self.kb = keyboard
        self.text_inputs = [self.file_name]

    def on_touch(self):
        for text_input in self.text_inputs:
            text_input.focus = False

    def on_pre_enter(self):
        self.info_button.opacity = 0
        self.display_profile = self.j.parameters_to_string()
        self.file_name.text = ""
        self.save_image.source = "save_file.png"

    def on_enter(self):
        self.kb.setup_text_inputs(self.text_inputs)

    def get_info(self):
        pass

    def go_back(self):
        self.shapecutter_sm.previous_screen()

    def next_screen(self):
        self.shapecutter_sm.position_tab()

    def prepare(self):
        self.shapecutter_sm.prepare_tab()

    def load(self):
        self.shapecutter_sm.load_tab()

    def define(self):
        self.shapecutter_sm.define_tab()

    def position(self):
        self.shapecutter_sm.position_tab()

    def check(self):
        self.shapecutter_sm.check_tab()

    def exit(self):
        self.shapecutter_sm.exit_shapecutter()

    def save_file(self):
        if not self.file_name.text == "":
            self.j.save_parameters(self.file_name.text)
            self.save_image.source = "thumbs_up.png"
        else:
            description = """Filename input is empty.

Please enter a name for your parameter profile."""
            WarningPopup(
                sm=self.shapecutter_sm,
                m=self.m,
                l=self.m.l,
                main_string=description,
                popup_width=400,
                popup_height=380,
                main_label_size_delta=40,
                button_layout_padding=[50, 25, 50, 0],
                main_label_h_align="left",
                main_layout_padding=[50, 20, 50, 20],
                main_label_padding=[20, 20],
            ).open()
