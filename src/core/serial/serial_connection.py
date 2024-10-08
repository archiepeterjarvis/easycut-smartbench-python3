"""
Created on 31 Jan 2018
@author: Ed
Module to manage all serial comms between pi (EasyCut s/w) and realtime arduino chip (GRBL f/w)
"""

import re
import sys
import threading
import time
from datetime import datetime, timedelta
from enum import Enum

import serial
import serial.tools.list_ports
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

from core.logging.logging_system import Logger
from core.serial import serial_conn
from ui.sequence_alarm import alarm_manager

BAUD_RATE = 115200
ENABLE_STATUS_REPORTS = True
GRBL_SCANNER_MIN_DELAY = 0.01


class MachineState(Enum):
    IDLE = "Idle"
    RUN = "Run"
    HOLD = "Hold"
    JOG = "Jog"
    HOME = "Home"
    CHECK = "Check"
    DOOR_0 = "Door:0"


class SerialConnection(EventDispatcher):
    setting_0 = NumericProperty(-1.0)
    setting_1 = NumericProperty(-1.0)
    setting_2 = NumericProperty(-1.0)
    setting_4 = NumericProperty(-1.0)
    setting_5 = NumericProperty(-1.0)
    setting_6 = NumericProperty(-1.0)
    setting_10 = NumericProperty(-1.0)
    setting_11 = NumericProperty(-1.0)
    setting_12 = NumericProperty(-1.0)
    setting_13 = NumericProperty(-1.0)
    setting_20 = NumericProperty(-1.0)
    setting_21 = NumericProperty(-1.0)
    setting_22 = NumericProperty(-1.0)
    setting_23 = NumericProperty(-1.0)
    setting_24 = NumericProperty(-1.0)
    setting_25 = NumericProperty(-1.0)
    setting_26 = NumericProperty(-1.0)
    setting_27 = NumericProperty(-1.0)
    setting_30 = NumericProperty(-1.0)
    setting_31 = NumericProperty(-1.0)
    setting_32 = NumericProperty(-1.0)
    setting_50 = NumericProperty(0.0)
    setting_51 = NumericProperty(-1.0)
    setting_100 = NumericProperty(0.0)
    setting_101 = NumericProperty(0.0)
    setting_102 = NumericProperty(0.0)
    setting_110 = NumericProperty(-1.0)
    setting_111 = NumericProperty(-1.0)
    setting_112 = NumericProperty(-1.0)
    setting_120 = NumericProperty(-1.0)
    setting_121 = NumericProperty(-1.0)
    setting_122 = NumericProperty(-1.0)
    setting_130 = NumericProperty(-1.0)
    setting_131 = NumericProperty(-1.0)
    STATUS_INTERVAL = 0.1
    s = None
    sm = None
    yp = None
    grbl_out = ""
    response_log = []
    suppress_error_screens = False
    FLUSH_FLAG = False
    write_command_buffer = []
    write_realtime_buffer = []
    write_protocol_buffer = []
    last_protocol_send_time = 0
    monitor_text_buffer = ""
    overload_state = 0
    prev_overload_state = 0
    is_ready_to_assess_spindle_for_shutdown = True
    power_loss_detected = False
    grbl_scanner_running = False
    spindle_on = BooleanProperty(False)
    vacuum_on = BooleanProperty(False)
    total_resets = None
    total_uptime_seconds = None
    total_distance = None

    def __init__(
            self,
            machine,
            screen_manager,
            settings_manager,
            localization,
            job,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # self.serial_conn = serial
        self.sm = screen_manager
        self.sett = settings_manager
        self.m = machine
        self.jd = job
        self.l = localization
        self.alarm = alarm_manager.AlarmSequenceManager(
            self.sm, self.sett, self.m, self.l, self.jd
        )
        self.FINAL_TEST = False
        self.register_event_type("on_serial_monitor_update")
        self.register_event_type("on_update_overload_peak")
        self.register_event_type("on_reset_runtime")
        self.register_event_type("on_check_job_finished")

    def update_current_screen(self, screen_name):
        def inner(dt):
            self.sm.current = screen_name

        Clock.schedule_once(inner, 0)

    def on_reset_runtime(self, *args):
        """Default callback. Needs to exist."""
        pass

    def on_serial_monitor_update(self, *args):
        """Default callback. Needs to exist."""
        pass

    def on_update_overload_peak(self, *args):
        """Default callback. Needs to exist."""
        pass

    def on_check_job_finished(self, *args):
        """Default callback. Needs to exist."""
        pass

    def __del__(self):
        if self.s:
            self.s.close()
        Logger.info("Serial connection destructor")

    def is_use_yp(self):
        if self.yp:
            return self.yp.use_yp
        else:
            return False

    def set_use_yp(self, val):
        if self.yp:
            self.yp.use_yp = val

    def get_serial_screen(self, serial_error):
        try:
            if self.sm.current != "serialScreen" and self.sm.current != "rebooting":
                self.sm.get_screen("serialScreen").error_description = self.l.get_str(
                    serial_error
                )
                self.update_current_screen("serialScreen")
        except:
            Logger.error(
                "Serial comms interrupted but no serial screen - are you in diagnostics mode?"
            )
            Logger.error("Serial error: " + str(serial_error))

    def establish_connection(self):
        ports_to_try = [port.device for port in serial_conn.SerialConnection.get_available_ports()]

        if sys.platform == 'linux':
            ports_to_try.insert(0, '/dev/ttyS0')  # this port is hidden as it is a 'non-present internal serial port'

        for port in ports_to_try:
            Logger.info(f"Trying to connect to SmartBench on port: {port}")
            if self.is_port_smartbench(port):
                break

        if not self.s:
            Logger.warning(f"Couldn't find a SmartBench connected to any of the ports: {ports_to_try}")
            return

        Logger.info(f"Connected to SmartBench on port: {self.s.port}")
        self.write_direct("\r\n\r\n", realtime=False, show_in_serial_montior=False)

    def is_port_smartbench(self, port):
        try:
            ser = serial.Serial(port=port, baudrate=BAUD_RATE, timeout=6, write_timeout=20)

            ser.close()
            ser.open()
            ser.write("\x18".encode("utf-8"))

            time.sleep(1)

            if not ser.in_waiting:
                ser.close()
                return False

            response = ser.read(ser.in_waiting).decode("utf-8")

            self.parse_grbl_response_on_connect(response)

            self.s = ser
        except serial.SerialException:
            Logger.exception(f"Failed to connect to port: {port}")
        except Exception:
            Logger.exception(f"Error when connecting to port: {port}")

    def parse_grbl_response_on_connect(self, response):
        """
        Parse the response from the SmartBench on connection.

        :param response: response from the SmartBench
        """
        for line in response.split("\n"):
            if line.startswith("Total resets:"):
                self.total_resets = line.split(":")[1].strip()
            elif line.startswith("Up time:"):
                self.total_uptime_seconds = line.split(":")[1].strip().replace("seconds", "")
            elif line.startswith("Total distance:"):
                self.total_distance = line.split(":")[1].strip().replace("mm", "")

    def is_connected(self):
        return self.s is not None and self.s.isOpen()

    def start_services(self, dt):
        Logger.info("Starting services")
        self.s.flushInput()
        self.next_poll_time = time.time()
        self.grbl_scanner_running = True
        t = threading.Thread(target=self.grbl_scanner)
        t.daemon = True
        t.start()
        self.m.bootup_sequence()
        self.m.starting_serial_connection = False

    VERBOSE_ALL_PUSH_MESSAGES = False
    VERBOSE_ALL_RESPONSE = True
    VERBOSE_STATUS = False

    def grbl_scanner(self, run_grbl_scanner_once=False):
        Logger.info("Running grbl_scanner thread")
        while self.grbl_scanner_running or run_grbl_scanner_once:
            if self.FLUSH_FLAG == True:
                self.s.flushInput()
                self.FLUSH_FLAG = False
            if self.next_poll_time < time.time():
                self.write_direct(
                    "?", realtime=True, show_in_serial_montior=False
                )
                self.next_poll_time = time.time() + self.STATUS_INTERVAL
            command_counter = 0
            for command in self.write_command_buffer:
                self.write_direct(*command)
                command_counter += 1
            del self.write_command_buffer[0:command_counter]
            realtime_counter = 0
            for realtime_command in self.write_realtime_buffer:
                self.write_direct(
                    realtime_command[0],
                    alt_display_text=realtime_command[1],
                    realtime=True,
                )
                realtime_counter += 1
            del self.write_realtime_buffer[0:realtime_counter]
            if (
                    self.write_protocol_buffer
                    and self.last_protocol_send_time + 0.05 < time.time()
            ):
                protocol_command = self.write_protocol_buffer[0]
                self.write_direct(
                    protocol_command[0],
                    alt_display_text=protocol_command[1],
                    protocol=True,
                )
                del self.write_protocol_buffer[0]
            if self.s.inWaiting():
                try:
                    rec_temp = self.s.readline().strip().decode("utf-8")
                except Exception as e:
                    Logger.critical("serial.readline exception:\n" + str(e))
                    rec_temp = ""
                    self.get_serial_screen("Could not read line from serial buffer.")
            else:
                rec_temp = ""
            if len(rec_temp):
                if self.VERBOSE_ALL_RESPONSE:
                    if rec_temp.startswith("<"):
                        Logger.info(rec_temp)
                    else:
                        Logger.info("< " + rec_temp)
                self.dispatch("on_serial_monitor_update", "rec", rec_temp)
                try:
                    if rec_temp.startswith(("ok", "error")):
                        self.process_grbl_response(rec_temp)
                    else:
                        self.process_grbl_push(rec_temp)
                except Exception as e:
                    Logger.critical("Process response exception: " + str(e))
                    self.get_serial_screen(
                        "Could not process grbl response. Grbl scanner has been stopped."
                    )
                    raise
                if (
                        self.is_job_streaming
                        and not self.m.is_machine_paused
                        and "Alarm" not in self.m.state()
                ):
                    if (
                            self.is_use_yp()
                            and self.m.has_spindle_health_check_passed()
                            and self.m.is_using_sc2()
                    ):
                        if (
                                self.digital_spindle_ld_qdA >= 0
                                and self.grbl_ln is not None
                                and self.digital_spindle_mains_voltage >= 0
                                and not self.in_inrush
                        ):
                            self.yp.add_status_to_yetipilot(
                                self.digital_spindle_ld_qdA,
                                self.digital_spindle_mains_voltage,
                                self.feed_override_percentage,
                                int(self.feed_rate),
                            )
                    if self.is_stream_lines_remaining:
                        self.stuff_buffer()
                    elif self.g_count == self.l_count:
                        self.end_stream()
                if (
                        self._ready_to_send_first_sequential_stream
                        and self.is_buffer_clear()
                ):
                    self._send_next_sequential_stream()
            run_grbl_scanner_once = False
        Logger.info("Killed grbl_scanner")
        self.m_state = "Off"

    GRBL_BLOCK_SIZE = 35
    RX_BUFFER_SIZE = 255
    is_job_streaming = False
    is_stream_lines_remaining = False
    job_to_check = []
    g_count = 0
    l_count = 0
    c_line = []
    stream_start_time = 0
    stream_end_time = 0
    stream_pause_start_time = 0
    stream_paused_accumulated_time = 0
    check_streaming_started = False
    NOT_SKELETON_STUFF = True

    def check_job(self, job_object):
        Logger.info("Checking job...")
        self.job_to_check = job_object
        self.m.enable_check_mode()
        self.set_use_yp(False)

        def check_job_inner_function():
            if self.m_state == "Check":
                self.check_streaming_started = True
                self.suppress_error_screens = True
                self.response_log = []
                self.run_job(job_object)
            else:
                Clock.schedule_once(lambda dt: check_job_inner_function(), 0.9)

        Clock.schedule_once(lambda dt: check_job_inner_function(), 0.9)

    def run_job(self, job_object):
        self.grbl_ln = None
        self.jd.grbl_mode_tracker = []
        self.jd.job_gcode_running = job_object
        Logger.info("Job starting...")
        if self.initialise_job() and self.jd.job_gcode_running:
            Clock.schedule_once(lambda dt: self.set_streaming_flags_to_true(), 2)
        elif not self.jd.job_gcode_running:
            Logger.info("Could not start job: File empty")
            self.sm.get_screen("go").reset_go_screen_prior_to_job_start()

    def initialise_job(self):
        if self.m_state != "Check":
            self.m.set_led_colour("GREEN")
            self.m.raise_z_axis_for_collet_access()
        self.FLUSH_FLAG = True
        self.NOT_SKELETON_STUFF = True
        time.sleep(0.1)
        self._reset_counters()
        return True

    def run_skeleton_buffer_stuffer(self, gcode_obj):
        self.grbl_ln = None
        self.jd.grbl_mode_tracker = []
        self.jd.job_gcode_running = gcode_obj
        self.m.set_pause(False)
        Logger.info("Skeleton buffer stuffing starting...")
        self.FLUSH_FLAG = True
        self.NOT_SKELETON_STUFF = False
        time.sleep(0.1)
        self._reset_counters()
        if self.jd.job_gcode_running:
            Clock.schedule_once(lambda dt: self.set_streaming_flags_to_true(), 2)

    def _reset_counters(self):
        self.l_count = 0
        self.g_count = 0
        self.c_line = []
        self.stream_pause_start_time = 0
        self.stream_paused_accumulated_time = 0
        self.stream_start_time = time.time()
        self.dispatch("on_reset_runtime")

    def set_streaming_flags_to_true(self):
        self.is_stream_lines_remaining = True
        self.is_job_streaming = True
        Logger.info("Job running")

    def stuff_buffer(self):
        while self.l_count < len(self.jd.job_gcode_running):
            line_to_go = self.add_line_number_to_gcode_line(
                self.jd.job_gcode_running[self.l_count], self.l_count
            )
            serial_space = self.RX_BUFFER_SIZE - sum(self.c_line)
            if len(line_to_go) + 1 <= serial_space:
                self.scrape_last_sent_modes(line_to_go)
                self.add_to_g_mode_tracker(
                    self.last_sent_motion_mode,
                    self.last_sent_feed,
                    self.last_sent_speed,
                )
                self.c_line.append(len(line_to_go) + 1)
                self.write_direct(line_to_go, show_in_serial_montior=False)
                self.l_count += 1
            else:
                return
        self.is_stream_lines_remaining = False

    last_line_executed = 0
    last_sent_motion_mode = ""
    last_sent_feed = 0
    last_sent_speed = 0
    feed_pattern = re.compile("F\\d+\\.?\\d*")
    speed_pattern = re.compile("S\\d+\\.?\\d*")
    g_motion_pattern = re.compile("((?<=G)|(?<=G0))([0-3])((?=\\D)|(?=$))")

    def add_line_number_to_gcode_line(self, line, i):
        return line if self.gcode_line_is_excluded(line) else "N" + str(i) + line

    def gcode_line_is_excluded(self, line):
        return (
                "(" in line
                or ")" in line
                or "$" in line
                or "AE" in line
                or "AF" in line
                or "*L" in line
        )

    def get_grbl_float(self, line, pattern, last_thing=None):
        match_obj = re.search(pattern, line)
        return float(match_obj.group()[1:]) if match_obj else last_thing

    def get_grbl_mode(self, line, grbl_pattern, last_thing=None):
        match_obj = re.search(grbl_pattern, line)
        return int(match_obj.group()) if match_obj else last_thing

    def scrape_last_sent_modes(self, line_to_go):
        self.last_sent_motion_mode = self.get_grbl_mode(
            line_to_go, self.g_motion_pattern, self.last_sent_motion_mode
        )
        self.last_sent_feed = self.get_grbl_float(
            line_to_go, self.feed_pattern, self.last_sent_feed
        )
        self.last_sent_speed = self.get_grbl_float(
            line_to_go, self.speed_pattern, self.last_sent_speed
        )

    def add_to_g_mode_tracker(self, motion, feed, speed):
        self.jd.grbl_mode_tracker += ((motion, feed, speed),)

    def remove_from_g_mode_tracker(self, line_diff):
        if line_diff:
            del self.jd.grbl_mode_tracker[:line_diff]

    def process_grbl_response(self, message):
        if self.suppress_error_screens:
            self.response_log.append(message)
        if message.startswith("error"):
            Logger.error("ERROR from GRBL: " + message)
            if not self.suppress_error_screens and self.sm.current != "errorScreen":
                self.sm.get_screen("errorScreen").message = message
                if self.sm.current == "alarmScreen":
                    self.sm.get_screen(
                        "errorScreen"
                    ).return_to_screen = self.sm.get_screen(
                        "alarmScreen"
                    ).return_to_screen
                else:
                    self.sm.get_screen("errorScreen").return_to_screen = self.sm.current
                self.update_current_screen("errorScreen")
        if self._process_oks_from_sequential_streaming:
            self._send_next_sequential_stream()
        elif self.is_job_streaming:
            self.g_count += 1
            if self.c_line != []:
                del self.c_line[0]

    def end_stream(self):
        Logger.info("Ending stream...")
        self.is_job_streaming = False
        self.is_stream_lines_remaining = False
        self.m.set_pause(False)
        self.set_use_yp(False)
        if self.NOT_SKELETON_STUFF:
            if self.m_state != "Check":
                if (
                        str(self.jd.job_gcode_running).count("M3")
                        > str(self.jd.job_gcode_running).count("M30")
                        and self.m.stylus_router_choice != "stylus"
                ):
                    Clock.schedule_once(lambda dt: self.update_machine_runtime(), 0.4)
                    self.sm.get_screen(
                        "spindle_cooldown"
                    ).return_screen = "job_feedback"
                    self.update_current_screen("spindle_cooldown")
                else:
                    self.m.turn_off_spindle()
                    time.sleep(0.4)
                    self.update_machine_runtime()
                    self.update_current_screen("job_feedback")
                if not self.jd.job_recovery_skip_recovery:
                    self.jd.write_to_recovery_file_after_completion()
            else:
                self.check_streaming_started = False
                self.m.disable_check_mode()
                self.suppress_error_screens = False
                self._reset_counters()
                self.job_to_check = []
                self.dispatch("on_check_job_finished", self.response_log)
        else:
            self._reset_counters()
            self.NOT_SKELETON_STUFF = True
        self.jd.job_gcode_running = []
        self.jd.grbl_mode_tracker = []
        self.grbl_ln = None
        self.jd.percent_thru_job = 100

    def cancel_stream(self):
        self.is_job_streaming = False
        self.is_stream_lines_remaining = False
        self.m.set_pause(False)
        self.jd.job_gcode_running = []
        self.set_use_yp(False)
        self.jd.grbl_mode_tracker = []
        cancel_line = self.grbl_ln
        self.grbl_ln = None
        if self.m_state != "Check":
            self.FLUSH_FLAG = True
            Clock.schedule_once(lambda dt: self.m.raise_z_axis_for_collet_access(), 0.5)
            Clock.schedule_once(lambda dt: self.m.turn_off_vacuum(), 1)
            time.sleep(0.4)
            time_taken_seconds = self.update_machine_runtime()
            if not self.jd.job_recovery_skip_recovery:
                self.jd.write_to_recovery_file_after_cancel(
                    cancel_line, time_taken_seconds
                )
        else:
            self.check_streaming_started = False
            self.m.disable_check_mode()
            self.suppress_error_screens = False
            self.job_to_check = []
            self.dispatch("on_check_job_finished", self.response_log)
            self.FLUSH_FLAG = True
            self._reset_counters()
        self.NOT_SKELETON_STUFF = True
        Logger.info("G-code streaming cancelled!")

    def update_machine_runtime(self):
        Logger.info("G-code streaming finished!")
        self.stream_end_time = time.time()
        time_taken_seconds = int(self.stream_end_time - self.stream_start_time) + 10
        only_running_time_seconds = (
                time_taken_seconds - self.stream_paused_accumulated_time
        )
        self.jd.pause_duration = str(
            timedelta(seconds=self.stream_paused_accumulated_time)
        ).split(".")[0]
        self.jd.total_time = str(timedelta(seconds=time_taken_seconds)).split(".")[0]
        self.jd.actual_runtime = str(
            timedelta(seconds=only_running_time_seconds)
        ).split(".")[0]
        Logger.info("Time elapsed: " + self.jd.total_time)
        Logger.info("Time paused: " + self.jd.pause_duration)
        Logger.info("Actual running time: " + self.jd.actual_runtime)
        if self.m.stylus_router_choice == "router":
            self.m.spindle_brush_use_seconds += only_running_time_seconds
            self.m.write_spindle_brush_values(
                self.m.spindle_brush_use_seconds, self.m.spindle_brush_lifetime_seconds
            )
        self.m.time_since_calibration_seconds += only_running_time_seconds
        self.m.write_calibration_settings(
            self.m.time_since_calibration_seconds,
            self.m.time_to_remind_user_to_calibrate_seconds,
        )
        self.m.time_since_z_head_lubricated_seconds += only_running_time_seconds
        self.m.write_z_head_maintenance_settings(
            self.m.time_since_z_head_lubricated_seconds
        )
        time_without_current_pause = (
                self.stream_pause_start_time
                - self.stream_start_time
                - self.stream_paused_accumulated_time
        )
        self._reset_counters()
        return time_without_current_pause

    m_state = StringProperty("Unknown")
    m_x = NumericProperty(0.0)
    m_y = NumericProperty(0.0)
    m_z = NumericProperty(0.0)
    x_change = False
    y_change = False
    z_change = False
    w_x = "0.0"
    w_y = "0.0"
    w_z = "0.0"
    wco_x = "0.0"
    wco_y = "0.0"
    wco_z = "0.0"
    g28_x = "0.0"
    g28_y = "0.0"
    g28_z = "0.0"
    grbl_ln = None
    spindle_speed = NumericProperty(0)
    feed_rate = 0
    feed_override_percentage = 100
    speed_override_percentage = 100
    spindle_load_voltage = None
    digital_spindle_ld_qdA = None
    digital_spindle_temperature = None
    digital_spindle_kill_time = None
    digital_spindle_mains_voltage = None
    digital_load_pattern = re.compile("Ld:\\d+,\\d+,\\d+,\\d+")
    inrush_counter = 0
    inrush_max = 20
    in_inrush = True
    spindle_freeload = None
    limit_x = False
    limit_X = False
    limit_y = False
    limit_Y = False
    limit_z = False
    probe = False
    dustshoe_is_closed = BooleanProperty(True)
    spare_door = False
    limit_Y_axis = False
    stall_X = False
    stall_Z = False
    stall_Y = False
    grbl_waiting_for_reset = False
    serial_blocks_available = GRBL_BLOCK_SIZE
    serial_chars_available = RX_BUFFER_SIZE
    print_buffer_status = True
    expecting_probe_result = False
    fw_version = StringProperty()
    hw_version = StringProperty()
    motor_driver_temp = None
    pcb_temp = None
    transistor_heatsink_temp = None
    microcontroller_mV = None
    LED_mV = None
    PSU_mV = None
    spindle_speed_monitor_mV = None
    sg_z_motor_axis = None
    sg_x_motor_axis = None
    sg_y_axis = None
    sg_y1_motor = None
    sg_y2_motor = None
    sg_x1_motor = None
    sg_x2_motor = None
    last_stall_tmc_index = None
    last_stall_motor_step_size = None
    last_stall_load = None
    last_stall_threshold = None
    last_stall_travel_distance = None
    last_stall_temperature = None
    last_stall_x_coord = None
    last_stall_y_coord = None
    last_stall_z_coord = None
    last_stall_status = None
    record_sg_values_flag = False
    spindle_serial_number = None
    spindle_production_year = None
    spindle_production_week = None
    spindle_firmware_version = None
    spindle_total_run_time_seconds = None
    spindle_brush_run_time_seconds = None
    spindle_mains_frequency_hertz = None
    grbl_initialisation_message = "^Grbl .+ \\['\\$' for help\\]$"
    measure_running_data = False
    running_data = []
    measurement_stage = 0
    spindle_health_check = False
    spindle_health_check_data = []

    def process_grbl_push(self, message):
        message = str(message)
        if self.VERBOSE_ALL_PUSH_MESSAGES:
            Logger.info(message)
        if message.startswith("<"):
            status_parts = message[1:-1].split("|")
            if (
                    status_parts[0] != "Idle"
                    and status_parts[0] != "Run"
                    and not status_parts[0].startswith("Hold")
                    and status_parts[0] != "Jog"
                    and status_parts[0] != "Alarm"
                    and not status_parts[0].startswith("Door")
                    and status_parts[0] != "Check"
                    and status_parts[0] != "Home"
                    and status_parts[0] != "Sleep"
            ):
                Logger.error("ERROR status parse: Status invalid: " + message)
                return
            if "|Pn:" not in message:
                self.limit_x = False
                self.limit_X = False
                self.limit_y = False
                self.limit_Y = False
                self.limit_z = False
                self.probe = False
                self.dustshoe_is_closed = True
                self.spare_door = False
                self.limit_Y_axis = False
                self.stall_X = False
                self.stall_Z = False
                self.stall_Y = False
            if (
                    not re.search(self.digital_load_pattern, message)
                    or self.digital_spindle_ld_qdA == 0
            ):
                self.inrush_counter = 0
                self.in_inrush = True
            elif self.inrush_counter < self.inrush_max:
                self.inrush_counter += 1
            elif self.inrush_counter == self.inrush_max and self.in_inrush:
                self.in_inrush = False
            self.m_state = status_parts[0]
            for part in status_parts:
                if part.startswith("MPos:"):
                    pos = part[5:].split(",")
                    try:
                        float(pos[0])
                        float(pos[1])
                        float(pos[2])
                    except:
                        Logger.exception(
                            "ERROR status parse: Position invalid: " + message
                        )
                        return
                    self.x_change = self.m_x != float(pos[0])
                    self.y_change = self.m_y != float(pos[1])
                    self.z_change = self.m_z != float(pos[2])
                    self.m_x = float(pos[0])
                    self.m_y = float(pos[1])
                    self.m_z = float(pos[2])
                elif part.startswith("WPos:"):
                    pos = part[5:].split(",")
                    try:
                        float(pos[0])
                        float(pos[1])
                        float(pos[2])
                    except:
                        Logger.exception(
                            "ERROR status parse: Position invalid: " + message
                        )
                        return
                    self.w_x = pos[0]
                    self.w_y = pos[1]
                    self.w_z = pos[2]
                elif part.startswith("WCO:"):
                    pos = part[4:].split(",")
                    try:
                        float(pos[0])
                        float(pos[1])
                        float(pos[2])
                    except:
                        Logger.exception(
                            "ERROR status parse: Position invalid: " + message
                        )
                        return
                    self.wco_x = pos[0]
                    self.wco_y = pos[1]
                    self.wco_z = pos[2]
                elif part.startswith("Bf:"):
                    buffer_info = part[3:].split(",")
                    try:
                        int(buffer_info[0])
                        int(buffer_info[1])
                    except:
                        Logger.exception(
                            "ERROR status parse: Buffer status invalid: " + message
                        )
                        return
                    if self.serial_chars_available != buffer_info[1]:
                        self.serial_chars_available = buffer_info[1]
                        self.print_buffer_status = True
                    if self.serial_blocks_available != buffer_info[0]:
                        self.serial_blocks_available = buffer_info[0]
                        self.print_buffer_status = True
                    if self.print_buffer_status == True:
                        self.print_buffer_status = False
                elif part.startswith("Ln:"):
                    value = part[3:]
                    try:
                        int(value)
                    except:
                        Logger.exception(
                            "ERROR status parse: Line number invalid: " + message
                        )
                        return
                    if self.grbl_ln is not None:
                        self.remove_from_g_mode_tracker(int(value) - self.grbl_ln)
                    else:
                        self.remove_from_g_mode_tracker(int(value))
                    self.grbl_ln = int(value)
                elif part.startswith("Pn:"):
                    pins_info = part.split(":")[1]
                    self.limit_x = "x" in pins_info
                    self.limit_X = "X" in pins_info
                    self.limit_z = "Z" in pins_info
                    if "P" in pins_info:
                        self.probe = True
                    else:
                        self.probe = False
                    if "g" in pins_info:
                        self.spare_door = True
                    else:
                        self.spare_door = False
                    if "G" in pins_info:
                        self.dustshoe_is_closed = False
                    else:
                        self.dustshoe_is_closed = True
                    if "Y" or "y" in pins_info:
                        if self.fw_version and int(self.fw_version.split(".")[0]) < 2:
                            self.limit_y = "y" in pins_info
                            self.limit_Y = "Y" in pins_info
                        else:
                            self.limit_Y_axis = "y" in pins_info
                            self.stall_Y = "Y" in pins_info
                    else:
                        self.limit_y = False
                        self.limit_Y = False
                        self.limit_Y_axis = False
                        self.stall_Y = False
                    self.stall_X = "S" in pins_info
                    self.stall_Z = "z" in pins_info
                    if self.stall_X or self.stall_Y or self.stall_Z:
                        self.alarm.sg_alarm = True
                    if (
                            "r" in pins_info
                            and not self.power_loss_detected
                            and sys.platform not in ["win32", "darwin"]
                    ):
                        self.m._grbl_door()
                        self.sm.get_screen("door").db.send_event(
                            2, "Power loss", "Connection loss: Check power and WiFi", 0
                        )
                        self.m.set_pause(True)
                        Logger.critical("Power loss or DC power supply")
                        self.power_loss_detected = True
                        Clock.schedule_once(
                            lambda dt: self.m.resume_from_a_soft_door(), 1
                        )
                elif part.startswith("Door") and self.m.is_machine_paused == False:
                    if part.startswith("Door:3"):
                        pass
                    else:
                        self.m.set_pause(True)
                        if self.sm.current != "door":
                            Logger.info("Hard " + self.m_state)
                            self.sm.get_screen(
                                "door"
                            ).return_to_screen = self.sm.current
                            self.update_current_screen("door")
                elif part.startswith("Ld:"):
                    spindle_feedback = part.split(":")[1]
                    if "," in spindle_feedback:
                        digital_spindle_feedback = spindle_feedback.split(",")
                        try:
                            int(digital_spindle_feedback[0])
                            int(digital_spindle_feedback[1])
                            int(digital_spindle_feedback[2])
                            int(digital_spindle_feedback[3])
                        except:
                            Logger.exception(
                                "ERROR status parse: Digital spindle feedback invalid: "
                                + message
                            )
                            return
                        self.digital_spindle_ld_qdA = int(digital_spindle_feedback[0])
                        self.digital_spindle_temperature = int(
                            digital_spindle_feedback[1]
                        )
                        self.digital_spindle_kill_time = int(
                            digital_spindle_feedback[2]
                        )
                        self.digital_spindle_mains_voltage = int(
                            digital_spindle_feedback[3]
                        )
                        if self.spindle_health_check and not self.in_inrush:
                            self.spindle_health_check_data.append(
                                self.digital_spindle_ld_qdA
                            )
                        if self.digital_spindle_kill_time >= 160:
                            overload_mV_equivalent_state = 0
                        elif self.digital_spindle_kill_time >= 80:
                            overload_mV_equivalent_state = 20
                        elif self.digital_spindle_kill_time >= 40:
                            overload_mV_equivalent_state = 40
                        elif self.digital_spindle_kill_time >= 20:
                            overload_mV_equivalent_state = 60
                        elif self.digital_spindle_kill_time >= 10:
                            overload_mV_equivalent_state = 80
                        elif self.digital_spindle_kill_time < 10:
                            overload_mV_equivalent_state = 100
                        else:
                            Logger.error("Killtime value not recognised")
                    else:
                        try:
                            int(spindle_feedback)
                        except:
                            Logger.exception(
                                "ERROR status parse: Analogue spindle feedback invalid: "
                                + message
                            )
                            return
                        self.spindle_load_voltage = int(spindle_feedback)
                        if self.spindle_load_voltage < 400:
                            overload_mV_equivalent_state = 0
                        elif self.spindle_load_voltage < 1000:
                            overload_mV_equivalent_state = 20
                        elif self.spindle_load_voltage < 1500:
                            overload_mV_equivalent_state = 40
                        elif self.spindle_load_voltage < 2000:
                            overload_mV_equivalent_state = 60
                        elif self.spindle_load_voltage < 2500:
                            overload_mV_equivalent_state = 80
                        elif self.spindle_load_voltage >= 2500:
                            overload_mV_equivalent_state = 100
                        else:
                            Logger.error("Overload value not recognised")
                    if overload_mV_equivalent_state != self.overload_state:
                        self.overload_state = overload_mV_equivalent_state
                        Logger.info(
                            "Overload state change: " + str(self.overload_state)
                        )
                        Logger.info("Load voltage: " + str(self.spindle_load_voltage))
                        try:
                            self.sm.get_screen("go").update_overload_label(
                                self.overload_state
                            )
                            if (
                                    20 <= self.overload_state < 100
                                    and self.is_ready_to_assess_spindle_for_shutdown
                            ):
                                self.prev_overload_state = self.overload_state
                                Clock.schedule_once(self.check_for_sustained_peak, 1)
                        except:
                            Logger.exception(
                                "Unable to update overload state on go screen"
                            )
                    if (
                            self.overload_state == 100
                            and self.is_ready_to_assess_spindle_for_shutdown
                    ):
                        self.is_ready_to_assess_spindle_for_shutdown = False
                        Clock.schedule_once(self.check_for_sustained_max_overload, 0.5)
                elif part.startswith("FS:"):
                    feed_speed = part[3:].split(",")
                    self.feed_rate = feed_speed[0]
                    if int(feed_speed[1]) != 0:
                        try:
                            is_spindle_sc2 = self.setting_51 == 1
                        except:
                            is_spindle_sc2 = False
                        if is_spindle_sc2:
                            self.spindle_speed = int(feed_speed[1])
                        else:
                            grbl_reported_rpm = int(feed_speed[1])
                            current_multiplier = (
                                    float(self.speed_override_percentage) / 100
                            )
                            current_gcode_rpm = self.m.correct_rpm(
                                grbl_reported_rpm / current_multiplier,
                                revert=True,
                                log=False,
                            )
                            current_running_rpm = current_gcode_rpm * current_multiplier
                            if current_running_rpm > self.m.maximum_spindle_speed():
                                current_running_rpm = self.m.maximum_spindle_speed()
                            if current_running_rpm < self.m.minimum_spindle_speed():
                                current_running_rpm = self.m.minimum_spindle_speed()
                            self.spindle_speed = int(current_running_rpm)
                    else:
                        self.spindle_speed = 0
                elif part.startswith("Ov:"):
                    values = part[3:].split(",")
                    try:
                        int(values[0])
                        int(values[1])
                        int(values[2])
                    except:
                        Logger.exception(
                            "ERROR status parse: Ov values invalid: " + message
                        )
                        return
                    self.feed_override_percentage = int(values[0])
                    self.speed_override_percentage = int(values[2])
                elif part.startswith("TC:"):
                    temps = part[3:].split(",")
                    try:
                        float(temps[0])
                        float(temps[1])
                    except:
                        Logger.exception(
                            "ERROR status parse: Temperature invalid: " + message
                        )
                        return
                    self.motor_driver_temp = float(temps[0])
                    self.pcb_temp = float(temps[1])
                    try:
                        float(temps[2])
                        self.transistor_heatsink_temp = float(temps[2])
                    except IndexError:
                        pass
                    except:
                        Logger.exception(
                            "ERROR status parse: Temperature invalid: " + message
                        )
                        return
                elif part.startswith("V:"):
                    voltages = part[2:].split(",")
                    try:
                        float(voltages[0])
                        float(voltages[1])
                        float(voltages[2])
                        float(voltages[3])
                    except:
                        Logger.exception(
                            "ERROR status parse: Voltage invalid: " + message
                        )
                        return
                    self.microcontroller_mV = float(voltages[0])
                    self.LED_mV = float(voltages[1])
                    self.PSU_mV = float(voltages[2])
                    self.spindle_speed_monitor_mV = float(voltages[3])
                elif part.startswith("SG:"):
                    sg_values = part[3:].split(",")
                    try:
                        int(sg_values[0])
                        int(sg_values[1])
                        int(sg_values[2])
                        int(sg_values[3])
                        int(sg_values[4])
                    except:
                        Logger.exception(
                            "ERROR status parse: SG values invalid: " + message
                        )
                        return
                    self.sg_z_motor_axis = int(sg_values[0])
                    self.sg_x_motor_axis = int(sg_values[1])
                    self.sg_y_axis = int(sg_values[2])
                    self.sg_y1_motor = int(sg_values[3])
                    self.sg_y2_motor = int(sg_values[4])
                    try:
                        int(sg_values[5])
                        int(sg_values[6])
                    except IndexError:
                        pass
                    except:
                        Logger.exception(
                            "ERROR status parse: SG values invalid: " + message
                        )
                        return
                    else:
                        self.sg_x1_motor = int(sg_values[5])
                        self.sg_x2_motor = int(sg_values[6])
                    if self.record_sg_values_flag:
                        self.m.temp_sg_array.append(
                            [
                                self.sg_z_motor_axis,
                                self.sg_x_motor_axis,
                                self.sg_y_axis,
                                self.sg_y1_motor,
                                self.sg_y2_motor,
                                self.sg_x1_motor,
                                self.sg_x2_motor,
                            ]
                        )
                    if self.FINAL_TEST:
                        if self.sm.has_screen("calibration_testing"):
                            self.sm.get_screen("calibration_testing").measure()
                        if self.sm.has_screen("overnight_testing"):
                            self.sm.get_screen("overnight_testing").measure()
                        if self.sm.has_screen("current_adjustment"):
                            self.sm.get_screen("current_adjustment").measure()
                elif part.startswith("SGALARM:"):
                    sg_alarm_parts = part[8:].split(",")
                    try:
                        int(sg_alarm_parts[0])
                        int(sg_alarm_parts[1])
                        int(sg_alarm_parts[2])
                        int(sg_alarm_parts[3])
                        int(sg_alarm_parts[4])
                        float(sg_alarm_parts[5])
                        float(sg_alarm_parts[6])
                        float(sg_alarm_parts[7])
                    except:
                        Logger.exception(
                            "ERROR status parse: SGALARM pins_info invalid: " + message
                        )
                        return
                    self.last_stall_tmc_index = int(sg_alarm_parts[0])
                    self.last_stall_motor_step_size = int(sg_alarm_parts[1])
                    self.last_stall_load = int(sg_alarm_parts[2])
                    self.last_stall_threshold = int(sg_alarm_parts[3])
                    self.last_stall_travel_distance = int(sg_alarm_parts[4])
                    self.last_stall_temperature = int(sg_alarm_parts[5])
                    self.last_stall_x_coord = float(sg_alarm_parts[6])
                    self.last_stall_y_coord = float(sg_alarm_parts[7])
                    self.last_stall_z_coord = float(sg_alarm_parts[8])
                    self.last_stall_status = message
                elif part.startswith("Sp:"):
                    spindle_statistics = part[3:].split(",")
                    try:
                        int(spindle_statistics[0])
                        int(spindle_statistics[1])
                        int(spindle_statistics[2])
                        int(spindle_statistics[3])
                        int(spindle_statistics[4])
                        int(spindle_statistics[5])
                        int(spindle_statistics[6])
                    except:
                        Logger.exception(
                            "ERROR status parse: Sp values invalid: " + message
                        )
                        return
                    self.spindle_serial_number = int(spindle_statistics[0])
                    self.spindle_production_year = int(spindle_statistics[1])
                    self.spindle_production_week = int(spindle_statistics[2])
                    self.spindle_firmware_version = int(spindle_statistics[3])
                    self.spindle_total_run_time_seconds = int(spindle_statistics[4])
                    self.spindle_brush_run_time_seconds = int(spindle_statistics[5])
                    self.spindle_mains_frequency_hertz = int(spindle_statistics[6])
                elif part.startswith("TREG:"):
                    tmc_registers = part[5:].split(",")
                    try:
                        int(tmc_registers[0])
                        int(tmc_registers[1])
                        int(tmc_registers[2])
                        int(tmc_registers[3])
                        int(tmc_registers[4])
                        int(tmc_registers[5])
                        int(tmc_registers[6])
                        int(tmc_registers[7])
                        int(tmc_registers[8])
                        int(tmc_registers[9])
                        int(tmc_registers[10])
                    except:
                        Logger.exception(
                            "ERROR status parse: TMC registers invalid: " + message
                        )
                        return
                    self.m.TMC_motor[int(tmc_registers[0])].shadowRegisters[0] = int(
                        tmc_registers[1]
                    )
                    self.m.TMC_motor[int(tmc_registers[0])].shadowRegisters[1] = int(
                        tmc_registers[2]
                    )
                    self.m.TMC_motor[int(tmc_registers[0])].shadowRegisters[2] = int(
                        tmc_registers[3]
                    )
                    self.m.TMC_motor[int(tmc_registers[0])].shadowRegisters[3] = int(
                        tmc_registers[4]
                    )
                    self.m.TMC_motor[int(tmc_registers[0])].shadowRegisters[4] = int(
                        tmc_registers[5]
                    )
                    self.m.TMC_motor[int(tmc_registers[0])].ActiveCurrentScale = int(
                        tmc_registers[6]
                    )
                    self.m.TMC_motor[
                        int(tmc_registers[0])
                    ].standStillCurrentScale = int(tmc_registers[7])
                    self.m.TMC_motor[
                        int(tmc_registers[0])
                    ].stallGuardAlarmThreshold = int(tmc_registers[8])
                    self.m.TMC_motor[int(tmc_registers[0])].max_step_period_us_SG = int(
                        tmc_registers[9]
                    )
                    self.m.TMC_motor[
                        int(tmc_registers[0])
                    ].temperatureCoefficient = int(tmc_registers[10])
                    self.m.TMC_motor[int(tmc_registers[0])].got_registers = True
                    try:
                        self.m.print_tmc_registers(int(tmc_registers[0]))
                    except:
                        Logger.exception("Could not print TMC registers")
                elif part.startswith("TCAL:M"):
                    [motor_index, all_cal_data] = part[6:].split(":")
                    all_cal_data_list = all_cal_data.strip(",").split(",")
                    try:
                        map(int, all_cal_data_list)
                    except:
                        Logger.exception(
                            "ERROR status parse: TCAL registers invalid: " + message
                        )
                        return
                    self.m.TMC_motor[int(motor_index)].calibration_dataset_SG_values = [
                        int(i) for i in all_cal_data_list[0:128]
                    ]
                    self.m.TMC_motor[
                        int(motor_index)
                    ].calibrated_at_current_setting = int(all_cal_data_list[128])
                    self.m.TMC_motor[int(motor_index)].calibrated_at_sgt_setting = int(
                        all_cal_data_list[129]
                    )
                    self.m.TMC_motor[int(motor_index)].calibrated_at_toff_setting = int(
                        all_cal_data_list[130]
                    )
                    self.m.TMC_motor[int(motor_index)].calibrated_at_temperature = int(
                        all_cal_data_list[131]
                    )
                    self.m.TMC_motor[
                        int(motor_index)
                    ].got_calibration_coefficients = True
                    try:
                        calibration_report_string = (
                                "-------------------------------------"
                                + "\n"
                                + "MOTOR ID: "
                                + str(int(motor_index))
                                + "\n"
                                + "Calibration coefficients: "
                                + str(all_cal_data_list[0:128])
                                + "\n"
                                + "Current setting: "
                                + str(
                            self.m.TMC_motor[
                                int(motor_index)
                            ].calibrated_at_current_setting
                        )
                                + "\n"
                                + "SGT setting: "
                                + str(
                            self.m.TMC_motor[
                                int(motor_index)
                            ].calibrated_at_sgt_setting
                        )
                                + "\n"
                                + "TOFF setting: "
                                + str(
                            self.m.TMC_motor[
                                int(motor_index)
                            ].calibrated_at_toff_setting
                        )
                                + "\n"
                                + "Calibration temperature: "
                                + str(
                            self.m.TMC_motor[
                                int(motor_index)
                            ].calibrated_at_temperature
                        )
                                + "\n"
                                + "-------------------------------------"
                        )
                        map(Logger.info, calibration_report_string.split("\n"))
                    except:
                        Logger.exception("Could not print calibration output")
            if self.VERBOSE_STATUS:
                Logger.debug(
                    f"state: {self.m_state} | x: {str(self.m_x)} | y: {str(self.m_y)} | z: {str(self.m_z)} | avail. blocks: {self.serial_blocks_available} | avail. chars: {self.serial_chars_available}"
                )
            if self.measure_running_data:
                try:
                    self.running_data.append(
                        [
                            int(self.measurement_stage),
                            self.m_x,
                            self.m_y,
                            self.m_z,
                            int(self.sg_x_motor_axis),
                            int(self.sg_y_axis),
                            int(self.sg_y1_motor),
                            int(self.sg_y2_motor),
                            int(self.sg_z_motor_axis),
                            int(self.motor_driver_temp),
                            int(self.pcb_temp),
                            int(self.transistor_heatsink_temp),
                            datetime.now(),
                            int(self.feed_rate),
                            self.sg_x1_motor,
                            self.sg_x2_motor,
                        ]
                    )
                except:
                    pass
        elif message.startswith("ALARM:"):
            self.grbl_waiting_for_reset = True
            Logger.warning("ALARM from GRBL: " + message)
            self.alarm.alert_user(message)
        elif message.startswith("$"):
            Logger.info(message)
            setting_and_value = message.split("=")
            setting = setting_and_value[0]
            value = float(setting_and_value[1])
            if setting == "$0":
                self.setting_0 = value
            elif setting == "$1":
                self.setting_1 = value
            elif setting == "$2":
                self.setting_2 = value
            elif setting == "$3":
                self.setting_3 = value
            elif setting == "$4":
                self.setting_4 = value
            elif setting == "$5":
                self.setting_5 = value
            elif setting == "$6":
                self.setting_6 = value
            elif setting == "$10":
                self.setting_10 = value
            elif setting == "$11":
                self.setting_11 = value
            elif setting == "$12":
                self.setting_12 = value
            elif setting == "$13":
                self.setting_13 = value
            elif setting == "$20":
                self.setting_20 = value
            elif setting == "$21":
                self.setting_21 = value
            elif setting == "$22":
                self.setting_22 = value
            elif setting == "$23":
                self.setting_23 = value
            elif setting == "$24":
                self.setting_24 = value
            elif setting == "$25":
                self.setting_25 = value
            elif setting == "$26":
                self.setting_26 = value
            elif setting == "$27":
                self.setting_27 = value
            elif setting == "$30":
                self.setting_30 = value
            elif setting == "$31":
                self.setting_31 = value
            elif setting == "$32":
                self.setting_32 = value
            elif setting == "$50":
                self.setting_50 = value
            elif setting == "$51":
                self.setting_51 = value
            elif setting == "$53":
                self.setting_53 = value
            elif setting == "$54":
                self.setting_54 = value
            elif setting == "$100":
                self.setting_100 = value
            elif setting == "$101":
                self.setting_101 = value
            elif setting == "$102":
                self.setting_102 = value
            elif setting == "$110":
                self.setting_110 = value
                self.sm.get_screen("home").common_move_widget.fast_x_speed = value
                self.sm.get_screen("home").common_move_widget.set_jog_speeds()
            elif setting == "$111":
                self.setting_111 = value
                self.sm.get_screen("home").common_move_widget.fast_y_speed = value
                self.sm.get_screen("home").common_move_widget.set_jog_speeds()
            elif setting == "$112":
                self.setting_112 = value
                self.sm.get_screen("home").common_move_widget.fast_z_speed = value
                self.sm.get_screen("home").common_move_widget.set_jog_speeds()
            elif setting == "$120":
                self.setting_120 = value
            elif setting == "$121":
                self.setting_121 = value
            elif setting == "$122":
                self.setting_122 = value
            elif setting == "$130":
                self.setting_130 = value
                self.m.grbl_x_max_travel = value
                self.m.set_jog_limits()
            elif setting == "$131":
                self.setting_131 = value
                self.m.grbl_y_max_travel = value
                self.m.set_jog_limits()
            elif setting == "$132":
                self.setting_132 = value
                self.m.grbl_z_max_travel = value
                self.m.set_jog_limits()
        elif message.startswith("["):
            stripped_message = message.replace("[", "").replace("]", "")
            if stripped_message.startswith("G28:"):
                pos = stripped_message[4:].split(",")
                self.g28_x = pos[0]
                self.g28_y = pos[1]
                self.g28_z = pos[2]
            elif stripped_message.startswith("G54:"):
                pos = stripped_message[4:].split(",")
                self.g54_x = pos[0]
                self.g54_y = pos[1]
                self.g54_z = pos[2]
            elif self.expecting_probe_result and stripped_message.startswith("PRB"):
                Logger.info(stripped_message)
                successful_probe = stripped_message.split(":")[2]
                if successful_probe:
                    z_machine_coord_when_probed = stripped_message.split(":")[1].split(
                        ","
                    )[2]
                    Logger.info(
                        "Probed at machine height: " + z_machine_coord_when_probed
                    )
                    self.m.probe_z_detection_event(z_machine_coord_when_probed)
                self.expecting_probe_result = False
            elif stripped_message.startswith("ASM CNC"):
                fw_hw_versions = stripped_message.split(";")
                try:
                    self.fw_version = fw_hw_versions[1].split(":")[1]
                    Logger.info("FW version: " + str(self.fw_version))
                except:
                    Logger.exception("Could not retrieve FW version")
                try:
                    self.hw_version = fw_hw_versions[2].split(":")[1]
                    Logger.info("HW version: " + str(self.hw_version))
                except:
                    Logger.exception("Could not retrieve HW version")
        elif re.match(self.grbl_initialisation_message, message):
            self.grbl_waiting_for_reset = False

    def check_for_sustained_max_overload(self, dt):
        try:
            if self.overload_state == 100 and sys.platform != "win32":
                self.m.stop_for_a_stream_pause("spindle_overload")
                self.sm.get_screen(
                    "spindle_shutdown"
                ).reason_for_pause = "spindle_overload"
                self.sm.get_screen("spindle_shutdown").return_screen = str(
                    self.sm.current
                )
                self.update_current_screen("spindle_shutdown")
                try:
                    self.dispatch("on_update_overload_peak", self.overload_state)
                except:
                    Logger.exception("Unable to update overload peak on go screen")
            else:
                self.is_ready_to_assess_spindle_for_shutdown = True
        except:
            Logger.exception(
                "Could not display spindle overload - are you on diagnostics mode?"
            )

    def check_for_sustained_peak(self, dt):
        if (
                self.overload_state >= self.prev_overload_state
                and self.overload_state != 100
        ):
            self.dispatch("on_update_overload_peak", self.prev_overload_state)

    is_sequential_streaming = False
    _sequential_stream_buffer = []
    _reset_grbl_after_stream = False
    _ready_to_send_first_sequential_stream = False
    _process_oks_from_sequential_streaming = False
    _dwell_time = 0.5
    _dwell_command = "G4 P" + str(_dwell_time)
    _micro_dwell_command = "G4 P" + str(0.01)

    def start_sequential_stream(
            self, list_to_stream, reset_grbl_after_stream=False, end_dwell=False
    ):
        if self.is_sequential_streaming:
            Logger.debug(f"already streaming...try again later ({list_to_stream})")
            Clock.schedule_once(
                lambda dt: self.start_sequential_stream(
                    list_to_stream, reset_grbl_after_stream, end_dwell
                ),
                0.3,
            )
            return
        self.is_sequential_streaming = True
        Logger.info("Start_sequential_stream")
        if reset_grbl_after_stream:
            list_to_stream.append(self._dwell_command)
        elif end_dwell:
            list_to_stream.append(self._micro_dwell_command)
        self._sequential_stream_buffer = list_to_stream
        self._reset_grbl_after_stream = reset_grbl_after_stream
        self._ready_to_send_first_sequential_stream = True

    def _send_next_sequential_stream(self):
        if self._ready_to_send_first_sequential_stream:
            self._ready_to_send_first_sequential_stream = False
            self._process_oks_from_sequential_streaming = True
        if self._sequential_stream_buffer:
            try:
                self.write_direct(self._sequential_stream_buffer[0])
                if self._after_grbl_settings_insert_dwell():
                    self._sequential_stream_buffer[0] = self._dwell_command
                else:
                    del self._sequential_stream_buffer[0]
            except IndexError:
                Logger.info("Sequential streaming buffer empty")
                return
        else:
            self._process_oks_from_sequential_streaming = False
            Logger.info("Sequential stream ended")
            if self._reset_grbl_after_stream:
                self._reset_grbl_after_stream = False
                self.m._grbl_soft_reset()
                Logger.info("GRBL Reset after sequential stream ended")
            self.is_sequential_streaming = False

    def _after_grbl_settings_insert_dwell(self):
        if self._sequential_stream_buffer[0].startswith("$"):
            try:
                if (
                        not self._sequential_stream_buffer[1].startswith("$")
                        and not self._sequential_stream_buffer[1] == self._dwell_command
                ):
                    return True
            except:
                return True
        return False

    def cancel_sequential_stream(self, reset_grbl_after_cancel=False):
        self._sequential_stream_buffer = []
        self._process_oks_from_sequential_streaming = False
        self._ready_to_send_first_sequential_stream = False
        if reset_grbl_after_cancel or self._reset_grbl_after_stream:
            self._reset_grbl_after_stream = False
            self.m._grbl_soft_reset()
            Logger.info("GRBL Reset after sequential stream cancelled")
        self.is_sequential_streaming = False

    def is_buffer_clear(self):
        if (
                int(self.serial_chars_available) == self.RX_BUFFER_SIZE
                and int(self.serial_blocks_available) == self.GRBL_BLOCK_SIZE
        ):
            return True
        return False

    def write_temp(self, serial_command, realtime=False, protocol=False):
        if isinstance(serial_command, str):
            if not serial_command.endswith("\n") and not protocol and not realtime:
                serial_command += "\n"
            serial_command = serial_command.encode()
        self.s.write(serial_command)

    def write_direct(self, serial_command, show_in_serial_montior=True, alt_display_text=None, realtime=False,
                     protocol=False):
        # Log the command
        if serial_command != '?':
            Logger.info(f"> {alt_display_text or serial_command}")

        # Show in serial monitor
        if show_in_serial_montior:
            self.dispatch("on_serial_monitor_update", "snd", alt_display_text or serial_command)

        # Track status of spindle, vacuum, etc
        if isinstance(serial_command, str):
            serial_command = serial_command.upper()
            if "M3" in serial_command:
                if self.m_state != "Check":
                    self.spindle_on = True
                if "S" in serial_command:
                    serial_command = self.compensate_spindle_speed_command(serial_command)
            elif "M5" in serial_command:
                self.spindle_on = False
            elif "AE" in serial_command:
                self.vacuum_on = True
            elif "AF" in serial_command:
                self.vacuum_on = False

        # Write the message to serial
        if self.s:
            self.write_temp(serial_command, realtime=realtime, protocol=protocol)

            if protocol:
                self.last_protocol_send_time = time.time()

    def write_command(self, serialCommand, **kwargs):
        self.write_command_buffer.append([serialCommand, kwargs])

    def write_realtime(self, serialCommand, alt_display_text=None):
        self.write_realtime_buffer.append([serialCommand, alt_display_text])

    def write_protocol(self, serialCommand, alt_display_text):
        self.write_protocol_buffer.append([serialCommand, alt_display_text])
        return serialCommand

    def compensate_spindle_speed_command(self, spindle_speed_line):
        """
        Modifies the spindle speed command by correcting the RPM value and replacing it in the command line.
        Correcting in this case refers to compensating for the conversion that happens from Z Head -> spindle

        Args:
            spindle_speed_line (str): The original spindle speed command line.

        Returns:
            str: The modified spindle speed command line with the corrected RPM value.
        """
        match = re.search("S(\\d+(\\.\\d+)?)", spindle_speed_line.upper())
        if match:
            spindle_speed = float(match.group(1))
        try:
            corrected_spindle_speed = self.m.correct_rpm(spindle_speed)
            new_line = re.sub(
                "(S\\d+(\\.\\d+)?)",
                "S" + str(corrected_spindle_speed),
                spindle_speed_line.upper(),
            )
            Logger.info("Modified spindle command: " + new_line)
            return new_line
        except:
            Logger.exception("Spindle speed command could not be modified")
        return spindle_speed_line
