import copy
import json
import os
import unittest

from bson import ObjectId

from pylibcklb.scripts.sendJson2Mongo import check_id, check_schema_version


def create_json_test_file(working_directory: str, json_filename: str, content: dict):
    with open(os.path.join(working_directory, json_filename), "w") as outfile:
        json.dump(content, outfile)


class Test(unittest.TestCase):

    def test_check_id_do_convert_id(self):
        data_origin = {"_id": "631dc81d12277d809b0dac77", "data": "tests"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = check_id(data_new)
        assert data_origin != data_new

    def test_check_id_do_not_convert_id(self):
        data_origin = {"_id": ObjectId(), "data": "tests"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = check_id(data_new)
        assert data_origin == data_new

    def test_check_id_insert_id(self):
        data_origin = {"data": "tests"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = check_id(data_new)
        assert data_new["_id"] is not None

    def test_check_schema_version_insert_schema_version(self):
        data_origin = {"data": "tests"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = check_schema_version(data_new)
        assert data_new["schema_version"] == 1

    def test_check_schema_version_convert_string(self):
        data_origin = {"data": "tests", "schema_version": "1"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = check_schema_version(data_new)
        assert data_new["schema_version"] == 1

    def test_check_schema_version_do_nothing(self):
        data_origin = {"data": "tests", "schema_version": 1}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = check_schema_version(data_new)
        assert data_new["schema_version"] == 1
