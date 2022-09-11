import logging
import unittest
import copy
import subprocess
import sys
from src.pylibcklb.mongo.sendJson2Mongo import check_id, apply_need_adaptations, get_arguments

from bson import ObjectId
import pytest


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

    def test_apply_need_adaptations_no_adaptations_needed(self):
        data_origin = {"_id": ObjectId(), "data": "tests"}

        # Create deep copy as other vise the pointer to the origin will also modify the origin object
        data_new = copy.deepcopy(data_origin)
        data_new = apply_need_adaptations(data_new)
        assert data_origin == data_new

    def test_get_arguments(self):
        sys.argv = ["tests", "-v"]
        arguments = get_arguments()
        assert arguments.loglevel == logging.INFO
        assert arguments.is_replacement == False
