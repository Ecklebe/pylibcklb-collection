import copy
import json
import logging
import os
import sys
import unittest
from unittest.mock import patch

import pytest
from bson import ObjectId

from pylibcklb.mongo.sendJson2Mongo import check_id, apply_need_adaptations, get_arguments, main, check_schema_version


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
        assert arguments.is_replacement is False

    def test_main(self):
        sys.argv = ["tests", "-v"]
        main()

    def test_main_no_arguments(self):
        sys.argv = ["tests"]
        with pytest.raises(SystemExit) as e:
            assert main()
        assert str(e.value) == "1"

    @patch('pylibcklb.mongo.sendJson2Mongo.close_connection_to_mongodb')
    @patch('pylibcklb.mongo.sendJson2Mongo.run_operation_on_collection')
    @patch('pylibcklb.mongo.sendJson2Mongo.load_data')
    @patch('pylibcklb.mongo.sendJson2Mongo.select_collection')
    @patch('pylibcklb.mongo.sendJson2Mongo.select_database')
    @patch('pylibcklb.mongo.sendJson2Mongo.create_connection_to_mongodb')
    @patch('pylibcklb.mongo.sendJson2Mongo.get_arguments')
    def test_main_mocked(self,
                         mock_get_arguments,
                         mock_create_connection_to_mongodb,
                         mock_select_database,
                         mock_select_collection,
                         mock_load_data,
                         mock_run_operation_on_collection,
                         mock_close_connection_to_mongodb):
        class TestArguments:
            working_directory = os.getcwd()
            connection_string = "mongodb://root:example@localhost:27017/"
            database_name = "test"
            collection_name = "test_send_data"
            json_filename = "test_data_1.json"
            is_replacement = False
            loglevel = logging.WARNING

        test_arguments = TestArguments()

        test_file_content_1 = {
            "_id": ObjectId(),
            "schema_version": 1,
            "data": "tests"
        }

        mock_get_arguments.return_value = test_arguments
        mock_create_connection_to_mongodb.return_value = None
        mock_select_database.return_value = None
        mock_select_collection.return_value = None
        mock_load_data = test_file_content_1
        mock_run_operation_on_collection.return_value = None
        mock_close_connection_to_mongodb.return_value = None

        main()
