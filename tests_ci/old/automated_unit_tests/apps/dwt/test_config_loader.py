import json
import os

import pytest
from mock import mock
from mock.mock import Mock

from apps.drywall_cutter_app.config import config_loader
from apps.drywall_cutter_app.config.config_classes import Configuration
from unit_test_base import UnitTestBase


class ConfigLoaderTestCases(UnitTestBase):
    def setUp(self):
        super(ConfigLoaderTestCases, self).setUp()
        self.dwt_config = config_loader.DWTConfig(Mock())

    def test_get_most_recent_config(self):
        recent_config = "my/path/to/recent/config.json"
        self.dwt_config.set_most_recent_config(recent_config)
        self.assertEqual(self.dwt_config.get_most_recent_config(),recent_config)
        with mock.patch("os.path.exists") as mocked_exists:
            mocked_exists.return_value = False
            self.assertEqual(self.dwt_config.get_most_recent_config(), None)

    def test_new_get_most_recent_config(self):
        with mock.patch("os.path.exists") as mocked_exists:
            mocked_exists.return_value = False

            self.assertEqual(None, self.dwt_config.get_most_recent_config())

    @pytest.mark.skip(reason="needs refactoring. active config has cleaned dimensions.")
    def test_new_start_up(self):
        with mock.patch(
            "apps.drywall_cutter_app.config.config_loader.DWTConfig.get_most_recent_config"
        ) as mocked_rc:
            mocked_rc.return_value = None

            with mock.patch("os.path.exists") as mocked_exists:
                mocked_exists.return_value = False
                #self.dwt_config.start_up()
                self.assertEqual(
                    json.dumps(
                        self.dwt_config.active_config, default=lambda o: o.__dict__
                    ),
                    json.dumps(Configuration.default(), default=lambda o: o.__dict__),
                )

            #self.dwt_config.start_up()
            with open(config_loader.TEMP_CONFIG_PATH, "r") as f:
                # Want to compare the entire thing, but had trouble so this is probably sufficient
                f_contents = f.read()
                self.assertEqual(
                    self.dwt_config.active_config.canvas_shape_dims.x,
                    json.loads(f_contents)["canvas_shape_dims"]["x"],
                )
                self.assertEqual(
                    self.dwt_config.active_config.cutter_type,
                    json.loads(f_contents)["cutter_type"],
                )

        with mock.patch("json.load") as mocked_load:
            mocked_load.return_value = {"most_recent_config": "test"}

    @pytest.mark.skip(reason="needs refactoring. active config has cleaned dimensions.")
    def test_start_up(self):
        # Mock os.listdir so
        with mock.patch("os.listdir") as mocked_listdir:
            mocked_listdir.return_value = []

            # Test loading DEFAULT Configuration if temp_config doesn't exist, and there's no recent configs
            with mock.patch("os.path.exists") as mocked_exists:
                mocked_exists.return_value = False
                active = json.dumps(self.dwt_config.active_config, default=lambda o: o.__dict__)
                default = json.dumps(Configuration.default(), default=lambda o: o.__dict__)
                self.assertEqual(active, default)

            # Test loading temp config, if there's no recent configs but temp_config does exist
            with open(config_loader.TEMP_CONFIG_PATH, "r") as f:
                # Want to compare the entire thing, but had trouble so this is probably sufficient
                f_contents = f.read()
                self.assertEqual(
                    self.dwt_config.active_config.canvas_shape_dims.x,
                    json.loads(f_contents)["canvas_shape_dims"]["x"],
                )
                self.assertEqual(
                    self.dwt_config.active_config.cutter_type,
                    json.loads(f_contents)["cutter_type"],
                )
