import queue
import sys
import time
import threading
import serial
import serial.tools.list_ports
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from core.logging.logging_system import Logger


class SerialConnection(EventDispatcher):
    last_status = StringProperty('', force_dispatch=True)

    def __init__(self, preferred_port, baudrate=115200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.preferred_port = preferred_port
        self.baudrate = baudrate
        self.serial = None
        self.serial_lock = threading.Lock()
        self.command_id_lock = threading.Lock()
        self.read_queue = queue.Queue()
        self.write_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_reading = False
        self.read_thread = None
        self.write_thread = None
        self.command_response_map = {}
        self.command_id = 0
        self.grbl_settings = {}

    @staticmethod
    def get_available_ports():
        ports = serial.tools.list_ports.comports()

        if not ports:
            raise RuntimeError("No serial ports available")

        if sys.platform == 'darwin':
            ports.pop(0)  # Pop bluetooth port out

        return ports

    def open(self):
        try:
            self.serial = serial.Serial(
                port=self.preferred_port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )

            self.is_reading = True

            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()

            self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
            self.write_thread.start()

            self._handle_startup_messages()
            return True
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return False

    def close(self):
        self.is_reading = False
        if self.read_thread:
            self.read_thread.join()
        if self.write_thread:
            self.write_thread.join()
        if self.serial and self.serial.is_open:
            self.serial.close()

    def reconnect(self):
        self.close()
        return self.open()

    def _read_loop(self):
        while self.is_reading:
            if self.serial and self.serial.in_waiting:
                with self.serial_lock:
                    line = self.serial.readline().decode("utf-8").strip()
                    self._process_response(line)
            time.sleep(0.01)

    def _process_response(self, response):
        Logger.debug(f"Processing response {response}")
        if response.startswith("<") and response.endswith(">"):
            # This is a status response
            Clock.schedule_once(lambda dt: self.last_status.setter(response), 0)
            if not self.response_queue.empty():
                command_id = self.response_queue.get()
                if command_id in self.command_response_map:
                    self.command_response_map[command_id].put(response)
        elif response.startswith("ok") or response.startswith("error"):
            if not self.response_queue.empty():
                command_id = self.response_queue.get()
                if command_id in self.command_response_map:
                    self.command_response_map[command_id].put(response)
        elif response.startswith("$"):
            key, val = response[1:].split("=")
            self.grbl_settings[key] = val
        else:
            self.read_queue.put(response)

    def _write_loop(self):
        while self.is_reading:
            try:
                command_id, data = self.write_queue.get(timeout=1)
                success = self._write(data)
                if success:
                    self.response_queue.put(command_id)
                else:
                    print(f"Failed to write data: {data}")
            except queue.Empty:
                pass

    def _write(self, data):
        with self.serial_lock:
            if self.serial and self.serial.is_open:
                Logger.debug(f"Writing data: {data}")
                self.serial.write(data.encode("utf-8") + b"\n")
                return True
        return False

    def _handle_startup_messages(self):
        """
        For reference on startup messages and how they're parsed, see:
        https://docs.google.com/document/d/1x1OvYjhGEIcWYbnOmEcxVfx6f87q3SUup0O4JP8BBEQ/edit#heading=h.kg4hkktokmib
        """
        startup_messages = []
        start_time = time.time()
        while time.time() - start_time < 2:
            try:
                message = self.read_queue.get(timeout=1)
                startup_messages.append(message)
            except queue.Empty:
                if not (6 <= len(startup_messages) < 9):
                    print(f"Failed to read startup messages (expected 6 <= x < 9, got x: {len(startup_messages)})")
                break

        # # Parse startup messages
        # total_resets = startup_messages[0].split(": ")[1]
        # up_time_seconds = startup_messages[1].split(": ")[1][:-7]  # 7 characters removed for 'seconds'
        # total_distance_mm = startup_messages[2].split(": ")[1][:-2]  # 2 characters removed for 'mm'
        #
        # sw_version = startup_messages[4].split("SW Ver:")[1].split("]")[0]
        # hw_version = startup_messages[4].split("HW Ver:")[1].split("]")[0]
        # grbl_version = startup_messages[5].split(" ")[1]
        #
        # for msg in startup_messages[6:]:
        #     print(msg)
        #     continue  # Catch things like 'Check Limits'

    def read(self, timeout=1):
        try:
            return self.read_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def flush(self):
        with self.serial_lock:
            if self.serial and self.serial.is_open:
                self.serial.flush()
                return True

    def send_command(self, command, timeout=5):
        with self.command_id_lock:
            command_id = self.command_id
            self.command_id += 1

        response_queue = queue.Queue()
        self.command_response_map[command_id] = response_queue
        self.write_queue.put((command_id, command))

        try:
            response = response_queue.get(timeout=timeout)
            if command == "?" and response == "ok":
                # For status requests, return the last known status
                return self.last_status
            return response
        except queue.Empty:
            print(f"Timeout waiting for response to command: {command}")
            if command == "?":
                # If it's a status request that timed out, return the last known status
                return self.last_status
            return None
        finally:
            del self.command_response_map[command_id]
