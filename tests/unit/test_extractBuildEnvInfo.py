import copy
import unittest

from bson import ObjectId

from pylibcklb.mongo.extractBuildEnvInfo import check_id


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
