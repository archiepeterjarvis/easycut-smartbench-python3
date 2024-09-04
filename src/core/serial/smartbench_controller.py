import threading
import time
from enum import Enum

from core.serial.serial_conn import SerialConnection


class StaticGRBLCommands(Enum):
    """Static GRBL commands (no parameters)"""
    LASER_ON = "AZ"
    LASER_OFF = "AX"
    HOME = "$H"
    GET_SETTINGS = "$$"


class LedColour(Enum):
    """Colour codes for the dust shoe LED"""
    RED = "FF0000"
    GREEN = "FFFF00"
    GREEN_HOMED = "11FF00"
    BLUE = "1100FF"
    WHITE = "FFFFFF"
    YELLOW = "FFFF00"
    ORANGE = "FF8000"
    MAGENTA = "FF00FF"
    OFF = "110000"


class SmartBenchController:
    def __init__(self, serial_conn: SerialConnection):
        self.serial_conn = serial_conn
        t = threading.Thread(target=self.poll_loop, daemon=True)
        t.start()

    def poll_loop(self):
        while True:
            self.get_status()
            time.sleep(1.0/13)

    def start_up_procedure(self):
        """
        Performs the initial start up procedure to get SmartBench ready.
        :return: None
        """
        self.serial_conn.flush()
        self.set_led_colour(LedColour.YELLOW)
        self.set_laser_status(False)
        self.get_grbl_settings()

    def set_led_colour(self, colour: LedColour):
        """
        Sets the colour of the dust shoe LED.
        :param colour: Colour of the dust shoe.
        :return: The GRBL response to the command.
        """
        return self.serial_conn.send_command(f"*L{colour.value}")

    def set_laser_status(self, laser_status: bool):
        """
        Turns the laser on or off.
        :param laser_status: True or False
        :return: The GRBL response to the command.
        """
        if laser_status:
            return self.serial_conn.send_command(StaticGRBLCommands.LASER_ON.value)
        else:
            return self.serial_conn.send_command(StaticGRBLCommands.LASER_OFF.value)

    def get_status(self):
        return self.serial_conn.send_command("?")

    def get_grbl_settings(self):
        """
        Sends '$$' to retrieve the GRBL settings.
        :return: The GRBL response to the command. (NOT THE SETTINGS)
        """
        return self.serial_conn.send_command(StaticGRBLCommands.GET_SETTINGS.value)

    def home(self):
        """
        Sends '$H' to home the SmartBench.
        :return: The GRBL response to the command.
        """
        return self.serial_conn.send_command(StaticGRBLCommands.HOME.value, timeout=15)

    def jog_absolute(self, feedrate, x=None, y=None, z=None):
        """
        Jog absolute to specific coordinates at specified feedrate.
        :param feedrate: Feedrate of the jog.
        :param x: X coordinate of the jog.
        :param y: Y coordinate of the jog.
        :param z: Z coordinate of the jog.
        :raises: ValueError if no coordinates are specified.
        :return: The GRBL response to the command.
        """
        if not x and not y and not z:
            raise ValueError("Either x or y or z must be specified.")

        #cmd = f"$J=G53 {f"X{x} " if x else ""}{f"Y{y} " if y else ""}{f"Z{z} " if z else ""}F{feedrate}"
        return self.serial_conn.send_command("", timeout=5)

    def jog_relative(self, feedrate, x=None, y=None, z=None):
        """
        Jog relative to specific coordinates at specified feedrate.
        :param feedrate: Feedrate of the jog.
        :param x: X coordinate of the jog.
        :param y: Y coordinate of the jog.
        :param z: Z coordinate of the jog.
        :raises: ValueError if no coordinates are specified.
        :return: The GRBL response to the command.
        """
        if not x and not y and not z:
            raise ValueError("Either x or y or z must be specified.")

        #cmd = f"$J=G91 {f"X{x} " if x else ""}{f"Y{y} " if y else ""}{f"Z{z} " if z else ""}F{feedrate}"
        return self.serial_conn.send_command("", timeout=5)

