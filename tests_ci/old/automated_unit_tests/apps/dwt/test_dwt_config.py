import os

from apps.drywall_cutter_app.config import config_loader
from apps.drywall_cutter_app.config.config_loader import CONFIGURATIONS_DIR
from core.logging.logging_system import Logger
from unit_test_base import UnitTestBase

try:
    import pytest
    from mock import Mock, MagicMock

except Exception as e:
    Logger.info(e)
    Logger.info("Can't import mocking packages, are you on a dev machine?")

"""
RUN WITH 
python -m pytest tests/automated_unit_tests/apps/dwt/test_dwt_config.py
FROM EASYCUT-SMARTBENCH DIR
"""


class TestDWTConfig(UnitTestBase):
    def test_load_config(self):
        dwt_config = config_loader.DWTConfig()

        dwt_config.load_config("test_config")

        assert dwt_config.active_config.shape_type == "rectangle"

    def test_save_config(self):
        dwt_config = config_loader.DWTConfig()

        dwt_config.load_config("test_config")

        new_path = os.path.join(CONFIGURATIONS_DIR,"test_config_saved")

        dwt_config.save_config(new_path)

        assert os.path.exists(new_path)

    def test_load_cutter(self):
        dwt_config = config_loader.DWTConfig()
        uid = "0001"
        dwt_config.load_cutter(uid)

        assert dwt_config.active_cutter.description.decode('utf-8') == self._app.profile_db.get_tool_name(uid)

    def test_save_temp_config(self):
        dwt_config = config_loader.DWTConfig()

        dwt_config.save_temp_config()

        assert os.path.exists(os.path.join("src", config_loader.TEMP_CONFIG_PATH))

    def test_on_parameter_change(self):
        dwt_config = config_loader.DWTConfig(Mock())
        dwt_config.on_parameter_change("shape_type", "circle")
        dwt_config.on_parameter_change("cutting_depths.material_thickness", 0.5)

        assert dwt_config.active_config.shape_type == "circle"
        assert dwt_config.active_config.cutting_depths.material_thickness == 0.5


