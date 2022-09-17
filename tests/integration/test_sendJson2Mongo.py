import json
import os

from bson import ObjectId
from pytest_mock_resources import create_mongo_fixture

from pylibcklb.mongo.sendJson2Mongo import send_file

mongo = create_mongo_fixture()


def create_json_test_file(working_directory: str, json_filename: str, content: dict):
    with open(os.path.join(working_directory, json_filename), "w") as outfile:
        json.dump(content, outfile)


def create_connection_string(mongo_credentials) -> str:
    host = mongo_credentials.host
    port = mongo_credentials.port
    username = mongo_credentials.username
    password = mongo_credentials.password
    auth_source = mongo_credentials.database
    return f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"


def test_send_data(mongo):
    class TestArguments:
        working_directory = os.getcwd()
        connection_string = create_connection_string(mongo.pmr_credentials)
        database_name = "test"
        collection_name = "test_send_data"
        json_filename = "test_data_1.json"
        is_replacement = False

    arguments = TestArguments()

    common_document_id = str(ObjectId())

    test_file_content_1 = {
        "_id": common_document_id,
        "schema_version": 1,
        "data": "tests"
    }
    create_json_test_file(arguments.working_directory, arguments.json_filename, test_file_content_1)
    send_file(arguments)
    os.remove(os.path.join(arguments.working_directory, arguments.json_filename))

    arguments.json_filename = "test_data_2.json"
    arguments.is_replacement = True
    test_file_content_2 = {
        "_id": common_document_id,
        "schema_version": 1,
        "data": "tests",
        "more_data": "This is more data from the document replacement"
    }
    create_json_test_file(arguments.working_directory, arguments.json_filename, test_file_content_2)
    send_file(arguments)
    os.remove(os.path.join(arguments.working_directory, arguments.json_filename))
