import os
import unittest

from bson import ObjectId

from pylibcklb.json.common import create_json_file, load_data
from pylibcklb.time.common import get_current_utc_time_ms


class Test(unittest.TestCase):

    def test_read_and_write(self):
        json_filename = "test_read_write.json"
        data_origin = {"_id": ObjectId(), "date": get_current_utc_time_ms()}
        create_json_file(os.getcwd(), json_filename, data_origin)
        data_new = load_data(os.getcwd(), json_filename)
        assert data_new == data_origin
        os.remove(os.path.join(os.getcwd(), json_filename))
