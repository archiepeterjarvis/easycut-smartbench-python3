from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_string(
    """

<IncorrectShutdownScreen>:

    title_label:title_label
    heading:heading
    correct_shutdown_steps:correct_shutdown_steps
    emergency_shutdown_warning:emergency_shutdown_warning
    next_button:next_button
    
    canvas:
        Color:
            rgba: hex('#E5E5E5FF')
        Rectangle:
            size: self.size
            pos: self.pos
            
    BoxLayout:
        orientation: 'vertical'
        size: self.parent.size
        pos: self.parent.pos
        padding: 0
        spacing: 0
        
        # Title section at the top
        BoxLayout:
            size_hint: (1, 0.125)
            orientation: 'horizontal'
            
            canvas.before:
                Color: 
                    rgba: hex('#1976D2FF')
                Rectangle: 
                    size: self.size
                    pos: self.pos
            
            Label:
                id: title_label
                size_hint_y: 1
                font_size: app.get_scaled_sp('30sp')
                markup: True
        
        # Main info section in the middle
        BoxLayout:
            size_hint: (1, 0.6)
            orientation: 'vertical'
            padding: app.get_scaled_tuple([10,10,10,10])
            
            FloatLayout:
                size_hint: (1, 0.6)
                padding: app.get_scaled_tuple([10,10,10,0])
                
                Image:
                    size_hint: (0.2,0.6)
                    source: "popup_error_visual.png"
                    center_x: self.parent.center_x
                    allow_stretch: True
                    size: app.get_scaled_tuple([20,20])
                    pos_hint: {'center_x': 0.1, 'center_y': 0.5}       
                
                BoxLayout:
                    orientation: 'vertical'
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5} 
                    Label:
                        id: heading
                        size_hint_y: 1
                        font_size: app.get_scaled_sp('25sp')
                        valign: 'middle'
                        halign: 'center'
                        text_size: self.parent.size
                        markup: True
                        color: hex('333333ff') 
                
            # Correct shutdown steps section
            BoxLayout:
                orientation: 'horizontal'   
                spacing: app.get_scaled_width(20)
                padding: app.get_scaled_tuple([10,0,0,0])
                
                BoxLayout:
                    Label:
                        id: correct_shutdown_steps
                        font_size: app.get_scaled_sp('20sp')
                        valign: 'middle'
                        text_size: self.parent.size
                        markup: True
                        color: hex('333333ff')
                        line_height: 1.5
                        
                Image:
                    size_hint: (0.2,1)
                    source: "correct-shutdown-qr.png"
                    center_x: self.parent.center_x
                    allow_stretch: True
                    pos_hint: {'center_x': 0.5}
             
            # Warning section        
            BoxLayout:
                orientation: 'horizontal'
                size_hint: (1,0.4)
                spacing: app.get_scaled_width(20)
                padding: app.get_scaled_tuple([0,0,0,0])        
                
                BoxLayout:
                    Label:
                        id: emergency_shutdown_warning
                        size_hint_y: 1
                        font_size: app.get_scaled_sp('25sp')
                        valign: 'middle'
                        halign: 'center'
                        text_size: self.parent.size
                        markup: True
                        color: hex('333333ff')
                    
        # 'I understand' button
        BoxLayout:
            size_hint: (0.4, 0.125)
            orientation: 'horizontal'
            pos_hint: {'center_x': 0.5}
            padding: app.get_scaled_tuple([0,0,0,10])
            
            Button:
                id: next_button
                on_press: root.next()
                background_normal: "next.png"
                background_down: "next.png"
                font_size: app.get_scaled_sp('28sp')
                
                
"""
)


class IncorrectShutdownScreen(Screen):
    def __init__(self, screen_manager, localization, start_sequence, **kwargs):
        super().__init__(**kwargs)
        self.start_seq = start_sequence
        self.l = localization
        self.sm = screen_manager
        self.update_strings()

    def next(self):
        self.start_seq.next_in_sequence()

    def update_strings(self):
        self.title_label.text = self.l.get_str("Power Off Warning")
        self.heading.text = self.l.get_str("SmartBench was not shut down correctly.")
        self.correct_shutdown_steps.text = (
            self.l.get_str("To avoid seeing this message again:")
            + "\n"
            + "  1.  "
            + self.l.get_str(
                "Shut down the Console using the power button in the lobby."
            )
            + "\n"
            + "  2.  "
            + self.l.get_str("Wait 20 seconds.")
            + "\n"
            + "  3.  "
            + self.l.get_str("Power off SmartBench using the red E-stop button.")
        )
        self.emergency_shutdown_warning.text = (
            "[b]"
            + self.l.get_str(
                "In the event of an emergency, always power down using the red E-stop button."
            )
            + "[/b]"
        )
        self.next_button.text = self.l.get_str("I understand")
