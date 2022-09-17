from bson import ObjectId
from pymongo import MongoClient


def check_id(data):
    if "_id" in data:
        if isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
    else:
        data["_id"] = ObjectId()
    return data


def check_schema_version(data):
    if "schema_version" in data:
        if isinstance(data["schema_version"], str):
            data["schema_version"] = int(data["schema_version"])
    else:
        data["schema_version"] = 1
    return data


def create_connection_to_mongodb(connection_string: str) -> MongoClient:
    return MongoClient(connection_string)


def close_connection_to_mongodb(client: MongoClient):
    client.close()


def select_database(client: MongoClient, database_name: str):
    return client[database_name]


def select_collection(database, collection_name: str):
    return database[collection_name]


def run_operation_on_collection(collection, is_replacement, data):
    if is_replacement:
        document_id = data.pop("_id")
        collection.replace_one({"_id": document_id}, data)
    else:
        collection.insert_one(data)


def create_connection_string(mongo_credentials) -> str:
    host = mongo_credentials.host
    port = mongo_credentials.port
    username = mongo_credentials.username
    password = mongo_credentials.password
    auth_source = mongo_credentials.database
    return f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
