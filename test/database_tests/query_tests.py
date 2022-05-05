try: 
    import unittest
    from mock import Mock, MagicMock

except:
    print("Can't import mocking packages, are you on a dev machine?")

import sys
sys.path.append('./src')

from datetime import datetime
from asmcnc.production.database.calibration_database import CalibrationDatabase

########################################################
# IMPORTANT!!
# Run from easycut-smartbench folder, with 
# python -m test.database_tests.query_tests


class SQLQueryTests(unittest.TestCase):
    """docstring for SQLQueryTests"""

    

    test_SG_dataset = [
            405,405,405,405,405,405,405,405,405,410,417,430,434,440,449,451,462,465,472,479,483,484,490,497,503,508,514,517,522,526,533,
            538,541,545,549,555,556,562,560,566,567,575,575,581,581,583,584,583,583,589,579,580,575,577,571,570,571,573,580,588,595,596,597,
            592,589,588,590,591,598,597,595,590,588,589,587,587,591,585,592,586,589,584,583,587,581,583,582,580,577,575,574,570,572,565,567,566,557,
            559,555,555,555,553,550,549,542,538,538,540,541,537,541,541,541,541,541,541,541,541,541,541,541,541,541,541,541,541,541,541
            ]

    params = [26,9,8,4500]
        
    coefficients = test_SG_dataset + params

    def setUp(self):
        # If the set_up method raises an exception while the test is running, 
        # the framework will consider the test to have suffered an error, 
        # and the runTest (or test_X_Name) method will not be executed.

        self.db = CalibrationDatabase()
        self.db.set_up_connection()

    # GENERAL TESTS

    def test_is_connected(self):
        self.assertIsNotNone(self.db.conn, "Database not connected :(")

    def test_get_ambient_temperature(self):
        self.assertIsNotNone(self.db.get_ambient_temperature(), "No temp :(")

    def test_get_stage_id_by_description(self):
        self.assertEqual(self.db.get_stage_id_by_description('CalibrationQC'), 1)

    # QC CALIBRATION TESTS

    # def test_setup_z_head_coefficients(self):
    #     self.db.setup_z_head_coefficients('zh2222', 4, 4)

    # def test_setup_lower_beam_coefficients(self):
    #     self.db.setup_lower_beam_coefficients('xl2222', 2, 1)

    # def test_insert_calibration_coefficients(self):
    #     self.db.insert_calibration_coefficients('zh2222', 4, 4, self.coefficients)

    # FETCH COEFFICIENTS TEST

    def test_get_lower_beam_coefficents(self):
        self.assertIsNotNone(self.db.get_lower_beam_coefficents('xl2222', 2, 1))

    # FINAL TEST TESTS

    # Serial numbers

    def test_get_serials_by_machine_serial(self):
        self.assertIsNotNone(self.db.get_serials_by_machine_serial('ys62222'))

    def test_get_all_serials_by_machine_serial(self):
        self.assertIsNotNone(self.db.get_all_serials_by_machine_serial('ys62222'))

    # Stages

    def test_insert_final_test_stage(self):
        self.db.insert_final_test_stage('ys62222', 5)

    def test_does_final_test_stage_already_exist_yarp(self):
        self.assertIsNotNone(self.db.does_final_test_stage_already_exist('622225'))

    def test_does_final_test_stage_already_exist_narp(self):
        self.assertIsNone(self.db.does_final_test_stage_already_exist('622228'))

    # Statistics

    def test_insert_final_test_statistics(self):
        statistics_list = ['ys62222', 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.db.insert_final_test_statistics(*statistics_list)

    # Statuses

    def test_insert_final_test_statuses(self):
                      # (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', %s, %s, %s, %s)
        status_list = [-1.0, -1.0, -1.0, -1, -1, -1, -3, -3, -3, -3, -3, 30, 45, 45, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 6000, 0, 0, 2]
        more_statuses = [status_list, status_list, status_list]
        self.db.insert_final_test_statuses('ys62222', 5, more_statuses)





        


if __name__ == "__main__":
    unittest.main()