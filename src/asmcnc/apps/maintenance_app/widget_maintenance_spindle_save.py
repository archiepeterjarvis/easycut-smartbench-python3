'''
Created on 19 August 2020
@author: Letty
widget to hold brush maintenance save and info
'''

import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

from asmcnc.apps.maintenance_app import popup_maintenance
from asmcnc.skavaUI import popup_info

Builder.load_string("""

<SpindleSaveWidget>

    BoxLayout:
        size_hint: (None, None)
        height: dp(350)
        width: dp(160)
        pos: self.parent.pos
        orientation: 'vertical'

        BoxLayout: 
	        size_hint: (None, None)
	        height: dp(175)
	        width: dp(160)
            padding: [15,21.5,13,21.5]
            ToggleButton:
                id: save_button
                on_press: root.save()
                size_hint: (None,None)
                height: dp(132)
                width: dp(132)
                background_color: [0,0,0,0]
                center: self.parent.center
                pos: self.parent.pos
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        id: save_image
                        source: "./asmcnc/apps/maintenance_app/img/save_button_132.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True

        BoxLayout: 
	        size_hint: (None, None)
	        height: dp(175)
	        width: dp(160)
            padding: [50,0,50,57.5]
	        Button:
	            background_color: hex('#F4433600')
	            on_press: root.get_info()
	            BoxLayout:
	                size_hint: (None,None)
	                height: dp(60)
	                width: dp(60)
	                pos: self.parent.pos
	                Image:
	                    source: "./asmcnc/apps/shapeCutter_app/img/info_icon.png"
	                    center_x: self.parent.center_x
	                    y: self.parent.y
	                    size: self.parent.width, self.parent.height
	                    allow_stretch: True

""")

class SpindleSaveWidget(Widget):

    def __init__(self, **kwargs):
    
        super(SpindleSaveWidget, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']
        self.l=kwargs['localization']

    def get_info(self):

        spindle_settings_info = (
                self.l.get_bold("Spindle brand") + \
                "[b]: [/b]" + \
                self.l.get_str("SmartBench will operate slightly differently depending on the type of spindle you are using.") + \
                " " + \
                self.l.get_str("It is important that you choose the option that matches the voltage and digital/manual specifications of your spindle.") + \
                "\n\n" + \
                self.l.get_bold("Spindle cooldown") + \
                "[b]: [/b]" + \
                self.l.get_str("The spindle needs to cool down after a job to prevent it from overheating, and to extend its lifetime.") + \
                " " + \
                self.l.get_str("We recommend the following cooldown settings:") + \
                "\n\n" + \
                "       " + \
                self.l.get_str("Yeti: 20,000 RPM; 10 seconds") + \
                "\n\n" + \
                "       " + \
                self.l.get_str("AMB: 10,000 RPM; 30 seconds") + \
                "\n\n" + \
                self.l.get_bold("CNC Stylus switch") + \
                "[b]: [/b]" + \
                self.l.get_str("When enabled, you will always be asked if you are using CNC Stylus or a Router at the start of every job.") + \
                "\n\n" + \
                self.l.get_bold("Spindle uptime") + \
                "[b]: [/b]" + \
                self.l.get_str("Press the button to display the spindle's uptime.")
            )

        popup_info.PopupScrollableInfo(self.sm, self.l, 750, spindle_settings_info)

    def save(self):

        try: 
            [brand, digital, voltage] = (self.sm.get_screen('maintenance').spindle_settings_widget.spindle_brand.text).rsplit(' ', 2)

            brand = brand[1:]
            voltage = voltage.strip('V')

            if 'digital' in digital: digital = True
            elif 'manual' in digital: digital = False
            else:
                brand_validation_error = (
                        self.l.get_str("Please select a valid spindle brand from the drop down.") + \
                        "\n\n" + \
                        self.l.get_str("If you can't find what you're looking for, please enter the version with a voltage and digital/manual option that matches what you have.")
                    )

                popup_info.PopupError(self.sm, self.l, brand_validation_error)
                return

        except:
            brand_validation_error = (
                    self.l.get_str("Please select a valid spindle brand from the drop down.") + \
                    "\n\n" + \
                    self.l.get_str("If you can't find what you're looking for, please enter the version with a voltage and digital/manual option that matches what you have.")
                )

            popup_info.PopupError(self.sm, self.l, brand_validation_error)
            return               




        try: 

            time = int(self.sm.get_screen('maintenance').spindle_settings_widget.spindle_cooldown_time.text)

            if (time >= 1 and time <= 60):
                pass

            else:
                time_validation_error = (
                        self.l.get_str("The spindle cooldown time should be between 1 and 60 seconds.") + \
                        "\n\n" + \
                        self.l.get_str("Please enter a new value.")
                    )

                popup_info.PopupError(self.sm, self.l, time_validation_error)
                return

        except: 

            time_validation_error = (
                    self.l.get_str("The spindle cooldown time should be a number between 1 and 60 seconds.") + \
                    "\n\n" + \
                    self.l.get_str("Please enter a new value.")
                )

            popup_info.PopupError(self.sm, self.l, time_validation_error)
            return



        try: 

            speed = int(self.sm.get_screen('maintenance').spindle_settings_widget.spindle_cooldown_speed.text)

            if (speed >= 10000 and speed <= 20000):
                pass

            else:
                speed_validation_error = (
                        self.l.get_str("The spindle cooldown speed should be between 10,000 and 20,000 RPM.") + \
                        "\n\n" + \
                        self.l.get_str("Please enter a new value.")
                    )

                popup_info.PopupError(self.sm, self.l, speed_validation_error)
                return

        except:
            speed_validation_error = (
                    self.l.get_str("The spindle cooldown speed should be a number between 10,000 and 20,000 RPM.") + \
                    "\n\n" + \
                    self.l.get_str("Please enter a new value.")
                )

            popup_info.PopupError(self.sm, self.l, speed_validation_error)
            return

        if self.m.write_spindle_cooldown_rpm_override_settings(self.sm.current_screen.spindle_settings_widget.rpm_override) and \
            self.m.write_spindle_cooldown_settings(brand, voltage, digital, time, speed) and \
            self.m.write_stylus_settings(self.sm.current_screen.spindle_settings_widget.stylus_switch.active):

            if self.m.is_machines_fw_version_equal_to_or_greater_than_version('2.2.8', 'Set $51 based on selected spindle'):
                if "SC2" in brand:
                    self.m.write_dollar_51_setting(1)
                else:
                    self.m.write_dollar_51_setting(0)

            saved_success = self.l.get_str("Settings saved!")
            popup_info.PopupMiniInfo(self.sm, self.l, saved_success)

        else:
            warning_message = (
                    self.l.get_str("There was a problem saving your settings.") + \
                    "\n\n" + \
                    self.l.get_str("Please check your settings and try again, or if the problem persists please contact the YetiTool support team.")
                )

            popup_info.PopupError(self.sm, self.l, warning_message)

        if voltage == '110': # localize me!
            spindle_voltage_info = (
                    self.l.get_str("When using a 110V spindle as part of your SmartBench, please be aware of the following:") + \
                    "\n\n" + \
                    self.l.get_str("110V spindles have a minimum speed of ~10,000 RPM.") + \
                    "\n\n" + \
                    self.l.get_str("SmartBench electronics are set up to work with a 230V spindle, so our software does a smart conversion to make sure the machine code we send is adjusted to control a 110V spindle.") + \
                    "\n\n" + \
                    self.l.get_str("The 5% spindle speed adjustments in the Job Screen cannot be converted for a 110V spindle, so they will not be able to adjust the speed by exactly 5%.") + \
                    " " + \
                    self.l.get_str("You will still be able to use the real time spindle speed feedback feature to assist your adjustment.")
                )
            
            popup_info.PopupInfo(self.sm, self.l, 780, spindle_voltage_info)

        # brands = ['YETI digital 230V', 'YETI digital 110V', 'AMB digital 230V', 'AMB manual 230V', 'AMB manual 110V']


    # spindle_brand = 'YETI' # String to hold brand name
    # spindle_voltage = 230 # Options are 230V or 110V
    # spindle_digital = False #spindle can be manual or digital
    # spindle_cooldown_time_seconds = 10 # YETI value is 10 seconds
    # spindle_cooldown_rpm = 12000 # YETI value was 20k, but has been lowered to 12k


# Mafell (YETI) - digital or manual; each one of those 110 or 230V - 4 variants total.

# AMB - 110V or 230V manual, 230V digital


















