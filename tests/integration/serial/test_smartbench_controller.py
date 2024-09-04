import unittest

from core.serial.smartbench_controller import SmartBenchController
from core.serial.serial_conn import SerialConnection


class SmartBenchControllerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.serial_conn = SerialConnection(preferred_port=SerialConnection.get_available_ports()[0].device)

        self.assertTrue(self.serial_conn.open())

        self.smartbench_controller = SmartBenchController(self.serial_conn)

    def tearDown(self):
        self.serial_conn.close()

    def test_home(self):
        self.smartbench_controller.home()

    def test_laser_on(self):
        self.smartbench_controller.set_laser_status(True)

    def test_laser_off(self):
        self.smartbench_controller.set_laser_status(False)

    def test_get_grbl_settings(self):
        self.smartbench_controller.get_grbl_settings()

        self.assertIsNotNone(self.serial_conn.grbl_settings)


if __name__ == '__main__':
    unittest.main()
