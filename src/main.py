"""
Created on 16 Nov 2017
@author: Ed
YetiTool's UI for SmartBench
www.yetitool.com
"""
import linecache
import os
import os.path
import sys
import threading
import traceback

from kivy.config import Config

from core.services import st_socket_connection, flurry_connection

# paths.create_paths()
Config.set("kivy", "keyboard_mode", "systemanddock")
if sys.platform.startswith("linux"):
    resolution = os.popen(" fbset | grep -oP 'mode \"\\K[^\"]+' ").read().strip()
    width, height = resolution.split("x")
    Config.set("graphics", "width", width)
    Config.set("graphics", "height", height)
else:
    Config.set("graphics", "width", "800")
    Config.set("graphics", "height", "480")
Config.set("graphics", "maxfps", "60")
# Config.set("kivy", "KIVY_CLOCK", "interrupt")
Config.write()
import logging
from core.managers.user_settings_manager import UserSettingsManager
from core.job.database.profile_database import ProfileDatabase
from kivy import Logger
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from core.managers.grbl_settings_manager import GRBLSettingsManagerSingleton
from ui.utils import scaling_utils, console_utils
from core.managers.model_manager import ProductCodes
from ui.popups.popup_manager import PopupManager
from core.managers.model_manager import ModelManagerSingleton
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window
from core.serial import router_machine
from apps import app_manager
from core.managers import settings_manager
from core.localization import Localization
from ui.keyboard import custom_keyboard
from core.job import job_data
from core.job.yetipilot.yetipilot import YetiPilot
from ui.screens import screen_home
from ui.screens import screen_local_filechooser
from ui.screens import screen_usb_filechooser
from ui.screens import screen_go
from ui.screens import screen_jobstart_warning
from ui.screens import screen_lobby
from ui.screens import screen_file_loading
from ui.screens import screen_check_job
from ui.screens import screen_error
from ui.screens import screen_serial_failure
from ui.screens import screen_mstate_warning
from ui.screens import screen_boundary_warning
from ui.screens import screen_rebooting
from ui.screens import screen_job_feedback
from ui.screens import screen_job_incomplete
from ui.screens import screen_door
from ui.screens import screen_squaring_manual_vs_square
from ui.screens import screen_homing_prepare
from ui.screens import screen_homing_active
from ui.screens import screen_squaring_active
from ui.screens import screen_spindle_shutdown
from ui.screens import screen_spindle_cooldown
from ui.screens import screen_stop_or_resume_decision
from ui.screens import screen_lift_z_on_pause_decision
from ui.screens import screen_tool_selection
from ui.screens import screen_job_recovery
from ui.screens import screen_nudge
from ui.screens import screen_recovery_decision
from ui.screens import screen_homing_decision
from ui.screens import screen_yeticut_lobby
from ui.screens import screen_dust_shoe_alarm

Cmport = "COM5"
initial_version = "v2.9.2"
config_flag = False


def check_and_update_config():
    if sys.platform != "win32" and sys.platform != "darwin":
        global config_flag
        config_flag = check_config_flag()
        if config_flag:
            ver0_configuration()
            check_ansible_status()


def check_config_flag():
    if (
            os.popen('grep "check_config=True" /home/pi/easycut-smartbench/src/config.txt')
                    .read()
                    .startswith("check_config=True")
    ):
        return True
    else:
        return False


def ver0_configuration():
    if (
            os.popen('grep "version=0" /home/pi/easycut-smartbench/src/config.txt')
                    .read()
                    .startswith("version=0")
    ):
        os.system(
            "cd /home/pi/easycut-smartbench/ && git update-index --skip-worktree /home/pi/easycut-smartbench/src/config.txt"
        )
        os.system(
            'sudo sed -i "s/config_skipped_by_git=False/config_skipped_by_git=True/" /home/pi/easycut-smartbench/src/config.txt'
        )
        os.system(
            'sudo sed -i "s/version=0/version='
            + initial_version
            + '/" /home/pi/easycut-smartbench/src/config.txt'
        )


def check_ansible_status():
    ansible_from_easycut = os.popen(
        'grep "ansible_from_easycut=True" /home/pi/easycut-smartbench/src/config.txt'
    ).read()
    if not ansible_from_easycut:
        os.system(
            "/home/pi/easycut-smartbench/ansible/templates/ansible-start.sh && sudo systemctl restart ansible.service"
        )
        console_utils.reboot()


check_and_update_config()
Builder.load_file("../resources/kv/scaled_kv.kv")
Logger.setLevel(logging.INFO)
os.system(
    "git remote set-url origin https://github.com/archiepeterjarvis/easycut-smartbench-python3"
)


class SkavaUI(App):
    test_no = 0
    width = Window.width
    height = Window.height if Window.height == 480 else Window.height - 32
    l = Localization()
    user_settings_manager = UserSettingsManager()
    profile_db = ProfileDatabase()

    def get_scaled_width(self, val):
        return scaling_utils.get_scaled_width(val)

    def get_scaled_height(self, val):
        return scaling_utils.get_scaled_height(val)

    def get_scaled_sp(self, val):
        return scaling_utils.get_scaled_sp(val)

    def get_scaled_tuple(self, tup, orientation="horizontal"):
        return scaling_utils.get_scaled_tuple(tup, orientation)

    def build(self):
        Logger.info("Starting App:")
        sm = ScreenManager(transition=NoTransition())
        kb = custom_keyboard.Keyboard(localization=self.l)
        sett = settings_manager.Settings(sm)
        jd = job_data.JobData(localization=self.l, settings_manager=sett)
        m = router_machine.RouterMachine(Cmport, sm, sett, self.l, jd)
        ModelManagerSingleton(m)
        GRBLSettingsManagerSingleton(m)
        yp = YetiPilot(screen_manager=sm, machine=m, job_data=jd, localization=self.l)
        db = flurry_connection.DatabaseEventManager(sm, m, sett)
        pm = PopupManager(sm, m, self.l)
        sm.pm = pm
        am = app_manager.AppManagerClass(
            sm, m, sett, self.l, kb, jd, db, config_flag, initial_version, pm
        )
        m.s.alarm.db = db
        m.s.yp = yp
        if ModelManagerSingleton().get_product_code() != ProductCodes.DRYWALLTEC:
            pass
            # sc = st_socket_connection.ServerConnection(sett)
        lobby_screen = screen_lobby.LobbyScreen(
            name="lobby",
            screen_manager=sm,
            machine=m,
            app_manager=am,
            localization=self.l,
        )
        home_screen = screen_home.HomeScreen(
            name="home",
            screen_manager=sm,
            machine=m,
            job=jd,
            settings=sett,
            localization=self.l,
            keyboard=kb,
        )
        local_filechooser = screen_local_filechooser.LocalFileChooser(
            name="local_filechooser", screen_manager=sm, job=jd, localization=self.l
        )
        usb_filechooser = screen_usb_filechooser.USBFileChooser(
            name="usb_filechooser", screen_manager=sm, job=jd, localization=self.l
        )
        go_screen = screen_go.GoScreen(
            name="go",
            screen_manager=sm,
            machine=m,
            job=jd,
            app_manager=am,
            database=db,
            localization=self.l,
            yetipilot=yp,
        )
        jobstart_warning_screen = screen_jobstart_warning.JobstartWarningScreen(
            name="jobstart_warning", screen_manager=sm, machine=m, localization=self.l
        )
        loading_screen = screen_file_loading.LoadingScreen(
            name="loading", screen_manager=sm, machine=m, job=jd, localization=self.l
        )
        checking_screen = screen_check_job.CheckingScreen(
            name="check_job", screen_manager=sm, machine=m, job=jd, localization=self.l
        )
        error_screen = screen_error.ErrorScreenClass(
            name="errorScreen",
            screen_manager=sm,
            machine=m,
            job=jd,
            database=db,
            localization=self.l,
        )
        serial_screen = screen_serial_failure.SerialFailureClass(
            name="serialScreen",
            screen_manager=sm,
            machine=m,
            win_port=Cmport,
            localization=self.l,
        )
        mstate_screen = screen_mstate_warning.WarningMState(
            name="mstate", screen_manager=sm, machine=m, localization=self.l
        )
        boundary_warning_screen = screen_boundary_warning.BoundaryWarningScreen(
            name="boundary", screen_manager=sm, machine=m, localization=self.l
        )
        rebooting_screen = screen_rebooting.RebootingScreen(
            name="rebooting", screen_manager=sm, localization=self.l
        )
        job_feedback_screen = screen_job_feedback.JobFeedbackScreen(
            name="job_feedback",
            screen_manager=sm,
            machine=m,
            database=db,
            job=jd,
            localization=self.l,
            keyboard=kb,
        )
        job_incomplete_screen = screen_job_incomplete.JobIncompleteScreen(
            name="job_incomplete",
            screen_manager=sm,
            machine=m,
            database=db,
            job=jd,
            localization=self.l,
            keyboard=kb,
        )
        door_screen = screen_door.DoorScreen(
            name="door",
            screen_manager=sm,
            machine=m,
            job=jd,
            database=db,
            localization=self.l,
        )
        squaring_decision_screen = (
            screen_squaring_manual_vs_square.SquaringScreenDecisionManualVsSquare(
                name="squaring_decision",
                screen_manager=sm,
                machine=m,
                localization=self.l,
            )
        )
        prepare_to_home_screen = screen_homing_prepare.HomingScreenPrepare(
            name="prepare_to_home", screen_manager=sm, machine=m, localization=self.l
        )
        homing_active_screen = screen_homing_active.HomingScreenActive(
            name="homing_active", screen_manager=sm, machine=m, localization=self.l
        )
        squaring_active_screen = screen_squaring_active.SquaringScreenActive(
            name="squaring_active", screen_manager=sm, machine=m, localization=self.l
        )
        spindle_shutdown_screen = screen_spindle_shutdown.SpindleShutdownScreen(
            name="spindle_shutdown",
            screen_manager=sm,
            machine=m,
            job=jd,
            database=db,
            localization=self.l,
        )
        spindle_cooldown_screen = screen_spindle_cooldown.SpindleCooldownScreen(
            name="spindle_cooldown", screen_manager=sm, machine=m, localization=self.l
        )
        stop_or_resume_decision_screen = (
            screen_stop_or_resume_decision.StopOrResumeDecisionScreen(
                name="stop_or_resume_job_decision",
                screen_manager=sm,
                machine=m,
                job=jd,
                database=db,
                localization=self.l,
            )
        )
        lift_z_on_pause_decision_screen = (
            screen_lift_z_on_pause_decision.LiftZOnPauseDecisionScreen(
                name="lift_z_on_pause_or_not",
                screen_manager=sm,
                machine=m,
                localization=self.l,
            )
        )
        tool_selection_screen = screen_tool_selection.ToolSelectionScreen(
            name="tool_selection", screen_manager=sm, machine=m, localization=self.l
        )
        job_recovery_screen = screen_job_recovery.JobRecoveryScreen(
            name="job_recovery",
            screen_manager=sm,
            machine=m,
            job=jd,
            localization=self.l,
            keyboard=kb,
        )
        nudge_screen = screen_nudge.NudgeScreen(
            name="nudge", screen_manager=sm, machine=m, job=jd, localization=self.l
        )
        recovery_decision_screen = screen_recovery_decision.RecoveryDecisionScreen(
            name="recovery_decision",
            screen_manager=sm,
            machine=m,
            job=jd,
            localization=self.l,
        )
        homing_decision_screen = screen_homing_decision.HomingDecisionScreen(
            name="homing_decision", screen_manager=sm, machine=m, localization=self.l
        )
        yeticut_lobby_screen = screen_yeticut_lobby.YeticutLobbyScreen(
            name="yeticut_lobby",
            screen_manager=sm,
            machine=m,
            localization=self.l,
            app_manager=am,
        )
        dust_shoe_alarm_screen = screen_dust_shoe_alarm.DustShoeAlarmScreen(
            sm, m, jd, db, self.l, name="dust_shoe_alarm"
        )
        sm.add_widget(lobby_screen)
        sm.add_widget(home_screen)
        sm.add_widget(local_filechooser)
        sm.add_widget(usb_filechooser)
        sm.add_widget(go_screen)
        sm.add_widget(jobstart_warning_screen)
        sm.add_widget(loading_screen)
        sm.add_widget(checking_screen)
        sm.add_widget(error_screen)
        sm.add_widget(serial_screen)
        sm.add_widget(mstate_screen)
        sm.add_widget(boundary_warning_screen)
        sm.add_widget(rebooting_screen)
        sm.add_widget(job_feedback_screen)
        sm.add_widget(job_incomplete_screen)
        sm.add_widget(door_screen)
        sm.add_widget(squaring_decision_screen)
        sm.add_widget(prepare_to_home_screen)
        sm.add_widget(homing_active_screen)
        sm.add_widget(squaring_active_screen)
        sm.add_widget(spindle_shutdown_screen)
        sm.add_widget(spindle_cooldown_screen)
        sm.add_widget(stop_or_resume_decision_screen)
        sm.add_widget(lift_z_on_pause_decision_screen)
        sm.add_widget(tool_selection_screen)
        sm.add_widget(job_recovery_screen)
        sm.add_widget(nudge_screen)
        sm.add_widget(recovery_decision_screen)
        sm.add_widget(homing_decision_screen)
        sm.add_widget(yeticut_lobby_screen)
        sm.add_widget(dust_shoe_alarm_screen)
        Logger.info("Screen manager activated: " + str(sm.current))
        if self.height == 768:
            root = BoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                size=(self.width, self.height + 32),
            )
            sm.size_hint = None, None
            sm.size = self.width, self.height
            root.add_widget(sm)
            return root
        return sm


def trace_func(frame, event, arg):
    if event == 'acquire':
        print(f"Thread {threading.current_thread().name} is attempting to acquire a lock")
    elif event == 'release':
        print(f"Thread {threading.current_thread().name} is releasing a lock")

    # Print the current line of code being executed
    if event == 'line':
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        line = linecache.getline(filename, lineno).strip()
        print(f"Thread {threading.current_thread().name}: {filename}:{lineno} - {line}")

    # Print stack trace for exceptions
    elif event == 'exception':
        print(f"Exception in thread {threading.current_thread().name}:")
        print(''.join(traceback.format_exception(*arg)))

    return trace_func


if __name__ == "__main__":
    import cProfile

    profiler = cProfile.Profile()
    try:
        profiler.enable()
        #threading.settrace(trace_func)
        SkavaUI().run()
    except KeyboardInterrupt:
        profiler.disable()
        profiler.dump_stats("yeti.pstat")
        raise
