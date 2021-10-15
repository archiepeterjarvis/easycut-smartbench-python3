from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
import sys, os
from asmcnc.skavaUI import popup_info

from asmcnc.apps.start_up_sequence.warranty_app.screens import \
screen_warranty_registration_1, \
screen_warranty_registration_2, \
screen_warranty_registration_3, \
screen_warranty_registration_4, \
screen_warranty_registration_5, \
screen_CNC_academy


class ScreenManagerWarranty(object):

    data_consent_app = None

    def __init__(self, app_manager, screen_manager, machine, localization):

        self.am = app_manager
        self.sm = screen_manager
        self.m = machine
        self.l = localization

    def load_warranty_app(self):

        if not self.sm.has_screen('warranty_1'):
            warranty_registration_1_screen = screen_warranty_registration_1.WarrantyScreen1(name = 'warranty_1', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(warranty_registration_1_screen)
        else:
            self.sm.get_screen('warranty_1').update_strings()

        if not self.sm.has_screen('warranty_2'):
            warranty_registration_2_screen = screen_warranty_registration_2.WarrantyScreen2(name = 'warranty_2', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(warranty_registration_2_screen)
        else:
            self.sm.get_screen('warranty_2').update_strings()

        if not self.sm.has_screen('warranty_3'):
            warranty_registration_3_screen = screen_warranty_registration_3.WarrantyScreen3(name = 'warranty_3', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(warranty_registration_3_screen)
        else:
            self.sm.get_screen('warranty_3').update_strings()

        if not self.sm.has_screen('warranty_4'):
            warranty_registration_4_screen = screen_warranty_registration_4.WarrantyScreen4(name = 'warranty_4', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(warranty_registration_4_screen)
        else:
            self.sm.get_screen('warranty_4').update_strings()

        if not self.sm.has_screen('warranty_5'):
            warranty_registration_5_screen = screen_warranty_registration_5.WarrantyScreen5(name = 'warranty_5', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(warranty_registration_5_screen)
        else:
            self.sm.get_screen('warranty_5').update_strings()

        if not self.sm.has_screen('cnc_academy'):
            CNC_academy_screen = screen_CNC_academy.CNCAcademyScreen(name = 'cnc_academy', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(CNC_academy_screen)
        else:
            self.sm.get_screen('cnc_academy').update_strings()

        if not self.sm.has_screen('reboot_to_apply_settings'):
            reboot_to_apply_language_settings_screen = screen_reboot_to_apply_language_settings.ApplySettingsScreen(name = 'reboot_to_apply_settings', warranty_manager = self, machine = self.m, localization = self.l)
            self.sm.add_widget(reboot_to_apply_language_settings_screen)
        else:
            self.sm.get_screen('reboot_to_apply_settings').update_strings()

    def open_warranty_app(self):
        self.load_warranty_app()
        self.sm.current = 'warranty_1' 

    def destroy_screen(self, screen_name):

        if self.sm.has_screen(screen_name):
            self.sm.remove_widget(self.sm.get_screen(screen_name))
            print (screen_name + ' deleted')