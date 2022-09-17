import os

# comes from the pymongo include bson
from bson.json_util import loads, dumps


def load_data(working_directory: str, json_filename: str):
    with open(os.path.join(working_directory, json_filename), 'r') as f:
        return loads(f.read())


def create_json_file(working_directory: str, json_filename: str, content: dict):
    with open(os.path.join(working_directory, json_filename), 'w') as file:
        file.write(dumps(content))
