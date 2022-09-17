#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from pylibcklb.json.common import load_data
from pylibcklb.logging.common import create_logger
from pylibcklb.mongo.common import check_id, check_schema_version, create_connection_to_mongodb, \
    close_connection_to_mongodb, select_database, select_collection, \
    run_operation_on_collection


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
        default=os.getenv("MONGODB_CONNECTION_STRING", None)
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


def apply_need_adaptations(data):
    data = check_id(data)
    data = check_schema_version(data)
    return data


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
        argument_parser.print_help()
        raise SystemExit(1)
    return argument_parser.parse_args()


def main():
    arguments = get_arguments()
    program_logger = create_logger(os.path.basename(__file__), arguments.loglevel)

    if arguments.connection_string:
        program_logger.info(f"Send data from file {arguments.json_filename} to the {arguments.database_name} database "
                            f"and {arguments.collection_name} collection.")
        send_file(arguments)
    else:
        program_logger.info(f"No connection string is given")
