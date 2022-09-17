import pytest
from pytest_mock_resources import MongoConfig


@pytest.fixture(scope='session')
def pmr_mongo_config():
    return MongoConfig(image="mongo:latest", port=28017, ci_port=29017, root_database="dev-mongo")
