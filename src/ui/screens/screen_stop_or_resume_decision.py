"""
Created March 2019

@author: Ed

Squaring decision: manual or auto?
"""

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from ui.popups import popup_info
from ui.popups.popups import BasicPopup, PopupType, InfoPopup

Builder.load_string(
    """

<StopOrResumeDecisionScreen>:

    pause_reason_label:pause_reason_label
    pause_description_label:pause_description_label

    canvas:
        Color: 
            rgba: hex('#E5E5E5FF')
        Rectangle: 
            size: self.size
            pos: self.pos         

    BoxLayout: 
        spacing: 0
        padding:[dp(0.025)*app.width, dp(0.0416666666667)*app.height]
        orientation: 'vertical'


        BoxLayout:
            orientation: 'vertical'
            spacing:0.0*app.height
            padding:[0, 0, 0, dp(0.0208333333333)*app.height]
            size_hint_y: 5
            

            Label:
                id: pause_reason_label
                size_hint_y: 0.6
                markup: True
                font_size: str(0.0375*app.width) + 'px' 
                valign: 'center'
                halign: 'center'
                size:self.texture_size
                text_size: self.size
                color: hex('#333333ff')
         
            Label:
                id: pause_description_label
                size_hint_y: 2.4
                markup: True
                font_size: str(0.0225*app.width) + 'px' 
                valign: 'center'
                halign: 'center'
                size:self.texture_size
                text_size: self.size
                color: hex('#333333ff')
     
        BoxLayout:
            orientation: 'horizontal'
            spacing: 0
            size_hint_y: 3

            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_x: 1
                background_color: hex('#FFFFFF00')
                on_press: root.cancel_job()
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "cancel_from_pause.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
                        
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_x: 0.3
                background_color: hex('#FFFFFF00')
                on_press: root.popup_help()
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "help_btn_yellow_round.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
                        
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_x: 1
                background_color: hex('#FFFFFF00')
                on_press: root.resume_job()
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "resume_from_pause.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
                        

"""
)


class StopOrResumeDecisionScreen(Screen):
    reason_for_pause = None
    return_screen = "lobby"
    qr_spindle_overload = "qr_spindle_overload.png"
    qr_yetipilot_low_feed = "qr_low_feed_rate.png"
    qr_yetipilot_no_data = "qr_no_spindle_data.png"
    qr_health_check = "qr_health_check_failed.png"
    qr_source = qr_spindle_overload

    def __init__(self, localization, database, job, machine, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.m = machine
        self.jd = job
        self.db = database
        self.l = localization

    def popup_help(self):
        info = (
            self.l.get_bold("Cancel")
            + "[b]"
            + " (X)"
            + "[/b]"
            + "\n"
            + self.l.get_str("Pressing cancel will cancel the job.")
            + "\n\n"
            + self.l.get_bold("Resume")
            + "[b]"
            + " (>)"
            + "[/b]"
            + "\n"
            + self.l.get_str(
                "Pressing resume will continue the job from the point at which it was paused."
            )
        )
        if self.reason_for_pause == "job_pause":
            info_popup = InfoPopup(
                sm=self.sm,
                m=self.m,
                l=self.l,
                title="Information",
                main_string=info,
                popup_width=500,
                popup_height=440,
            )
            info_popup.open()
        else:
            info += (
                "\n\n"
                + self.l.get_bold("Scan the QR code to learn more about this error.")
                + "\n"
                + self.l.get_bold("Or visit <URL>").replace(
                    "<URL>", "www.yetitool.com/support > Knowledge Base"
                )
            )
            qr_popup = BasicPopup(
                sm=self.sm,
                m=self.m,
                l=self.l,
                title="Information",
                main_string=info,
                popup_type=PopupType.QR,
                popup_image=self.qr_source,
                popup_image_size_hint=(1, 1.5),
                popup_width=500,
                popup_height=440,
                main_label_size_delta=40,
                main_label_h_align="left",
                main_label_padding=(10, 10),
                main_layout_spacing=10,
                main_layout_padding=10,
                button_layout_padding=(150, 20, 150, 0),
                button_layout_spacing=15,
                button_one_text="Ok",
                button_one_background_color=(76 / 255.0, 175 / 255.0, 80 / 255.0, 1.0),
            )
            qr_popup.open()

    def on_pre_enter(self):
        self.update_strings()

    def update_strings(self):
        try:
            self.sm.get_screen("go").start_or_pause_button_image.source = "resume.png"
        except:
            pass
        if self.reason_for_pause == "job_pause":
            self.pause_reason_label.text = self.l.get_str("SmartBench is paused.")
            self.pause_description_label.text = self.l.get_str(
                "You may resume, or cancel the job at any time."
            )
        if self.reason_for_pause == "spindle_overload":
            self.pause_reason_label.text = self.l.get_str(
                "Spindle motor was overloaded!"
            ).replace(self.l.get_str("overloaded"), self.l.get_bold("overloaded"))
            self.pause_description_label.text = (
                self.l.get_str(
                    "SmartBench has automatically stopped the job because it detected the spindle was starting to overload."
                )
                + "\n"
                + self.l.get_str(
                    "You may resume, but we recommend you allow the spindle to cool off first."
                ).replace(
                    self.l.get_str("You may resume"), self.l.get_bold("You may resume")
                )
                + "\n"
                + self.l.get_str(
                    "Try adjusting the speeds and feeds to reduce the load on the spindle, or adjust the job to reduce chip loading."
                )
                + " "
                + self.l.get_str(
                    "Check extraction, air intake, exhaust, worn brushes, work-holding, blunt cutters or anything else which may strain the spindle."
                )
            )
            self.qr_source = self.qr_spindle_overload
        if self.reason_for_pause == "yetipilot_low_feed":
            self.pause_reason_label.text = self.l.get_str("Feed rate too slow!")
            self.pause_description_label.text = (
                self.l.get_str(
                    "YetiPilot has tried to reduce the feed rate to less than 10% of the feed rate in the job file."
                )
                + "\n\n"
                + self.l.get_str(
                    "This may be because the chosen feed rate in the job file was set too high, or because of a problem with the cut which means the Spindle motor's target power cannot be reached."
                )
                + " "
                + self.l.get_str('Press "?" for more information.')
                + "\n\n"
                + self.l.get_bold(
                    "We recommend that you cancel the job and correct the issue."
                )
                + " "
                + self.l.get_str(
                    "Or, you may resume the job with YetiPilot initially disabled."
                ).replace(
                    self.l.get_str("Or, you may resume"),
                    self.l.get_bold("Or, you may resume"),
                )
                + " "
                + self.l.get_str("If you choose to resume, SmartBench may struggle.")
            )
            self.qr_source = self.qr_yetipilot_low_feed
        if self.reason_for_pause == "yetipilot_spindle_data_loss":
            self.pause_reason_label.text = self.l.get_str("Can't read spindle data!")
            self.pause_description_label.text = (
                self.l.get_str(
                    "Cannot read the data from the SC2 Spindle motor, which is needed to measure the load."
                )
                + "\n\n"
                + self.l.get_str(
                    "Please check that you are using your SC2 Spindle motor, and check that your data cable is connected."
                )
                + " "
                + self.l.get_str('Press "?" for more information.')
                + "\n\n"
                + self.l.get_str(
                    "You may resume the job with YetiPilot disabled, or cancel the job altogether."
                ).replace(
                    self.l.get_str("You may resume"), self.l.get_bold("You may resume")
                )
            )
            self.qr_source = self.qr_yetipilot_no_data
        if self.reason_for_pause == "spindle_health_check_failed":
            self.pause_reason_label.text = self.l.get_str(
                "Spindle motor health check failed!"
            )
            self.pause_description_label.text = (
                self.l.get_str("Spindle motor load is too high.")
                + "\n\n"
                + self.l.get_str(
                    "Please check that your SC2 Spindle motor is clamped correctly."
                )
                + "\n\n"
                + self.l.get_str(
                    "If you continue without resolving the issue, it will result in accelerated wear of the Spindle motor."
                )
                + "\n\n"
                + self.l.get_str(
                    "You may resume the job with YetiPilot disabled, or cancel the job altogether."
                ).replace(
                    self.l.get_str("You may resume"), self.l.get_bold("You may resume")
                )
            )
            self.qr_source = self.qr_health_check
        self.update_font_size(self.pause_description_label)

    def cancel_job(self):
        popup_info.PopupConfirmJobCancel(self.sm, self.l)

    def confirm_job_cancel(self):
        self.m.stop_from_soft_stop_cancel()
        self.m.s.is_ready_to_assess_spindle_for_shutdown = True
        self.sm.get_screen("job_incomplete").prep_this_screen(
            "cancelled", event_number=False
        )
        self.sm.current = "job_incomplete"

    def resume_job(self):
        if self.reason_for_pause == "yetipilot_low_feed":
            self.sm.get_screen("go").yp_widget.disable_yeti_pilot()
        self.sm.current = self.return_screen

    def update_font_size(self, value):
        text_length = self.l.get_text_length(value.text)
        if text_length > 700:
            value.font_size = 0.02 * Window.width
        elif text_length > 500:
            value.font_size = 0.02125 * Window.width
        else:
            value.font_size = 0.0225 * Window.width
