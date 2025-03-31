import unittest, pandas
from unittest.mock import patch
from compiler.helpers.dataset import checkRowEmpty, parseDatasetFile, dataset
from compiler.config import (
    DATASET_PATH
)



class TestDataset(unittest.TestCase):

    """
    Testcases for checking if a dataset row is empty
    """
    def testRowWithEmptyValues(self):
        row = ["value1", "", "value3", None, "value5", "value6", "", None, "value9", "value10"]
        self.assertTrue(checkRowEmpty(row))

    def testRowWithAllValues(self):
        row = ["value1", "value2", "value3", "value4", "value5", "value6", "value7", "value8", "value9", "value10"]
        self.assertFalse(checkRowEmpty(row))

    def testRowWithMissingColumns(self):
        row = ["value1", "value2", "value3"]
        self.assertTrue(checkRowEmpty(row))  # Some indexes are out of range

    def testRowWithNoneValues(self):
        row = [None, None, None, None, None, None, None, None, None, None]
        self.assertTrue(checkRowEmpty(row))

    def testRowWithAllEmptyStrings(self):
        row = ["", "", "", "", "", "", "", "", "", ""]
        self.assertTrue(checkRowEmpty(row))

    """
    Testcases for parsing the dataset
    """



if __name__ == '__main__':
    unittest.main()