#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys

try:
    from pymongo import MongoClient
    from bson import ObjectId
    from bson.json_util import loads
except ModuleNotFoundError:
    # Do not install the bson package as it is incompatible with pymongo
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymongo"])
    from pymongo import MongoClient
    from bson import ObjectId
    from bson.json_util import loads


def create_logger(application_name: str, default_level=logging.NOTSET):
    # create logger
    logger = logging.getLogger(application_name)
    logger.setLevel(default_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def create_argumentparser(program_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=program_name,
        description=f"The help of {program_name}",
        epilog="")
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    parser.add_argument(
        '-conn', '--connection-string',
        help="Connection string to create a connection to the mongodb",
        action="store", dest="connection_string",
        default=os.getenv("MONGODB_CONNECTION_STRING")
    )
    parser.add_argument(
        '-db', '--database',
        help="Database name which to use",
        action="store", dest="database_name"
    )
    parser.add_argument(
        '-cn', '--collection-name',
        help="Collection name in the mongodb to send data to",
        action="store", dest="collection_name"
    )
    parser.add_argument(
        '-r', '--replacement',
        help="To a replacement instead of a insert a document",
        action="store_const", dest="is_replacement", const=True,
        default=False,
    )
    parser.add_argument(
        '-json-filename',
        help="Define a specific name for the json output file",
        action="store", dest="json_filename",
    )
    parser.add_argument(
        '-w', '--working-dir',
        help="Define a specific name for the json output file",
        action="store", dest="working_directory",
        default=os.getcwd(),
    )
    return parser


def create_connection_to_mongodb(connection_string: str) -> MongoClient:
    return MongoClient(connection_string)


def close_connection_to_mongodb(client: MongoClient):
    client.close()


def select_database(client: MongoClient, database_name: str):
    return client[database_name]


def select_collection(database, collection_name: str):
    return database[collection_name]


def load_data(working_directory: str, json_filename: str):
    with open(os.path.join(working_directory, json_filename), 'r') as f:
        return loads(f.read())


def check_id(data):
    if "_id" in data:
        if isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
    else:
        data["_id"] = ObjectId()
    return data


def check_schema_version(data):
    if "schema_version" in data:
        if isinstance(data["_id"], str):
            data["schema_version"] = int(data["_id"])
    else:
        data["schema_version"] = 1
    return data


def apply_need_adaptations(data):
    data = check_id(data)
    data = check_schema_version(data)
    return data


def run_operation_on_collection(collection, is_replacement, data):
    if is_replacement:
        document_id = data.pop("_id")
        collection.replace_one({"_id": document_id}, data)
    else:
        collection.insert_one(data)


def send_file(args):
    client = create_connection_to_mongodb(args.connection_string)
    db = select_database(client, args.database_name)
    collection = select_collection(db, args.collection_name)
    data = load_data(args.working_directory, args.json_filename)
    data = apply_need_adaptations(data)
    run_operation_on_collection(collection, args.is_replacement, data)
    close_connection_to_mongodb(client)


def get_arguments():
    argument_parser = create_argumentparser(os.path.basename(__file__))
    if len(sys.argv) == 1:
        argument_parser.print_help(sys.stderr)
        sys.exit(1)
    return argument_parser.parse_args()


def main():
    arguments = get_arguments()
    program_logger = create_logger(os.path.basename(__file__), arguments.loglevel)

    program_logger.info(f"Send data from file {arguments.json_filename} to the {arguments.database_name} database "
                        f"and {arguments.collection_name} collection.")
    send_file(arguments)


if __name__ == "__main__":
    main()
