import unittest
from unittest.mock import call

import mock

from core.serial import smartbench_controller


class SmartBenchControllerUnitTests(unittest.TestCase):
    def setUp(self):
        self.mock_serial = mock.MagicMock()
        self.smartbench_controller = smartbench_controller.SmartBenchController(self.mock_serial)

    def test_start_up_procedure(self):
        self.smartbench_controller.start_up_procedure()
        self.mock_serial.flush.assert_called_once()

        expected_send_command_calls = [
            call(f"*L{smartbench_controller.LedColour.YELLOW.value}"),  # Set LEDS to yellow
            call(smartbench_controller.StaticGRBLCommands.LASER_OFF.value),  # Turn laser off
            call(smartbench_controller.StaticGRBLCommands.GET_SETTINGS.value)  # Get settings
        ]

        self.assertEqual(expected_send_command_calls, self.mock_serial.send_command.mock_calls)

    def test_jog_absolute_no_coordinates(self):
        with self.assertRaises(ValueError):
            self.smartbench_controller.jog(smartbench_controller.JogMode.ABSOLUTE, 100)

    def test_jog_absolute_x_coordinate(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.ABSOLUTE, 100, x=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G53 X100 F100", timeout=5)

    def test_jog_absolute_y_coordinate(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.ABSOLUTE, 100, y=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G53 Y100 F100", timeout=5)

    def test_jog_absolute_z_coordinate(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.ABSOLUTE, 100, z=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G53 Z100 F100", timeout=5)

    def test_jog_absolute_xyz_coordinates(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.ABSOLUTE, 100, x=100, y=100, z=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G53 X100 Y100 Z100 F100", timeout=5)

    def test_jog_relative_no_coordinates(self):
        with self.assertRaises(ValueError):
            self.smartbench_controller.jog(smartbench_controller.JogMode.RELATIVE, 100)

    def test_jog_relative_x_coordinate(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.RELATIVE, 100, x=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G91 X100 F100", timeout=5)

    def test_jog_relative_y_coordinate(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.RELATIVE, 100, y=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G91 Y100 F100", timeout=5)

    def test_jog_relative_z_coordinate(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.RELATIVE, 100, z=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G91 Z100 F100", timeout=5)

    def test_jog_relative_xyz_coordinates(self):
        self.smartbench_controller.jog(smartbench_controller.JogMode.RELATIVE, 100, x=100, y=100, z=100)
        self.mock_serial.send_command.assert_called_once_with("$J=G91 X100 Y100 Z100 F100", timeout=5)


if __name__ == '__main__':
    unittest.main()
