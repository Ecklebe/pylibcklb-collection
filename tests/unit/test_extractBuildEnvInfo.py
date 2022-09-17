import copy
import logging
import os
import sys
import unittest

import pytest
from bson import ObjectId

from pylibcklb.scripts.extractBuildEnvInfo import main, apply_need_adaptations, get_arguments


class Test(unittest.TestCase):

    def test_apply_need_adaptations_no_adaptations_needed(self):
        data_origin = {"_id": ObjectId(), "data": "tests", "schema_version": 1}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = apply_need_adaptations(data_new)
        assert data_origin == data_new

    def test_apply_need_adaptations_adaptations_needed(self):
        data_origin = {"_id": ObjectId(), "data": "tests", "schema_version": "1"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = apply_need_adaptations(data_new)
        assert data_new["_id"] == data_origin["_id"]
        assert data_new["data"] == data_origin["data"]
        assert data_new["schema_version"] == 1

    def test_get_arguments(self):
        sys.argv = ["tests", "-v"]
        arguments = get_arguments()
        assert arguments.loglevel == logging.INFO

    def test_main(self):
        sys.argv = ["tests", "-v"]
        main()

    def test_get_system_information(self):
        sys.argv = ["tests", "-v", "-esi"]
        main()

    def test_save_to_json(self):
        sys.argv = ["tests", "-v", "-json"]
        main()
        os.remove(os.path.join(os.getcwd(), "build-env.json"))

    def test_main_no_arguments(self):
        sys.argv = ["tests"]
        with pytest.raises(SystemExit) as e:
            assert main()
        assert str(e.value) == "1"
