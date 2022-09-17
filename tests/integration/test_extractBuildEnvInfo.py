import logging
import os
import sys

from pytest_mock_resources import create_mongo_fixture

from pylibcklb.mongo.common import create_connection_string
from pylibcklb.scripts.extractBuildEnvInfo import send_information_to_mongo, main

mongo = create_mongo_fixture()


def test_get_system_information():
    sys.argv = ["tests", "-v", "-esi"]
    main()


def test_get_system_information():
    sys.argv = ["tests", "-v", "-ewi"]
    main()


def test_main_mocked(mongo):
    class TestArguments:
        working_directory = os.getcwd()
        connection_string = create_connection_string(mongo.pmr_credentials)
        database_name = "test"
        collection_name = "test_send_data"
        json_filename = "test_data_1.json"
        is_replacement = False
        loglevel = logging.WARNING

    test_arguments = TestArguments()
    send_information_to_mongo(test_arguments, {"system_information": None})
