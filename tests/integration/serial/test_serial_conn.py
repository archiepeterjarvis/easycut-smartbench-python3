import time
import unittest

from core.serial.serial_conn import SerialConnection

AVAILABLE_PORTS = SerialConnection.get_available_ports()
PREFERRED_PORT = AVAILABLE_PORTS[0].device


"""
Integration tests for the SerialConnection class.

These tests require a physical machine connected to the computer running the tests. 
This can be a real bench, a rig, or a mini rig.

Ensure to close the connection after each test to avoid conflicts with other tests.
"""


class SerialConnectionIntegrationTests(unittest.TestCase):
    def test_open(self):
        serial_conn = SerialConnection(PREFERRED_PORT)

        self.assertTrue(serial_conn.open())

        serial_conn.close()

    def test_close(self):
        serial_conn = SerialConnection(PREFERRED_PORT)

        self.assertTrue(serial_conn.open())

        serial_conn.close()

        self.assertFalse(serial_conn.serial.is_open)

    def test_reconnect(self):
        serial_conn = SerialConnection(PREFERRED_PORT)

        self.assertTrue(serial_conn.open())
        self.assertTrue(serial_conn.reconnect())

        serial_conn.close()

    def test_read(self):
        serial_conn = SerialConnection(PREFERRED_PORT)

        self.assertTrue(serial_conn.open())

        status = serial_conn.send_command("?")

        self.assertIsNotNone(status)
        self.assertFalse(status.startswith("ok") or status.startswith("error"))

        serial_conn.close()

    def test_read_settings(self):
        serial_conn = SerialConnection(PREFERRED_PORT)

        self.assertTrue(serial_conn.open())

        response = serial_conn.send_command("$$")

        self.assertEqual(response, "ok")
        self.assertIsNotNone(serial_conn.grbl_settings)

        serial_conn.close()

    def test_write(self):
        serial_conn = SerialConnection(PREFERRED_PORT)

        self.assertTrue(serial_conn.open())

        # Test example GCODE
        response = serial_conn.send_command("G21")
        self.assertIsNotNone(response)
        self.assertTrue(response.startswith("ok"))

        # Test poll (?)
        status = serial_conn.send_command("?")
        self.assertIsNotNone(status)
        self.assertTrue(status.startswith("<") and status.endswith(">"))

        # Test example GCODE movement
        response = serial_conn.send_command("G0 X10 Y10 F3000")
        self.assertIsNotNone(response)
        self.assertTrue(response.startswith("ok"))

        time.sleep(0.5)

        # Ensure machine has moved
        new_status = serial_conn.send_command("?")
        self.assertIsNotNone(new_status)
        self.assertNotEqual(status, new_status)

        serial_conn.close()

    def test_get_available_ports(self):
        self.assertIsNotNone(SerialConnection.get_available_ports())


if __name__ == '__main__':
    unittest.main()
