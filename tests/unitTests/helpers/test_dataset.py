import unittest, pandas #type: ignore
from unittest.mock import patch
from compiler.helpers.dataset import checkRowEmpty, parseDatasetFile, dataset
from compiler.config import (
    DATASET_PATH
)

import sys
print(sys.executable)

class TestDatasetEmptyRows(unittest.TestCase):
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

class TestParsingDataset(unittest.TestCase):
    """
    Testcases for parsing the dataset
    """
    def setUp(self):
        dataset.clear()
    
    @patch('pandas.read_excel')
    def testSuccessfulParsing(self, mock_read_excel):
        mock_df = pandas.DataFrame({
            'Column1': ['Header', 'Value1', 'Value2'],
            'Column2': ['Header', 'Data1', 'Data2'],
            'Column3': ['Header', 'Info1', 'Info2'],
            'Column4': ['Header', 'Info1', 'Info2'],
            'Column5': ['Header', 'Info1', 'Info2'],
            'Column6': ['Header', 'Info1', 'Info2'],
            'Column7': ['Header', 'Info1', 'Info2'],
            'Column8': ['Header', 'Info1', 'Info2'],
            'Column9': ['Header', 'Info1', 'Info2'],
            'Column10': ['Header', 'Info1', 'Info2']
        })
        mock_read_excel.return_value = mock_df
        
        parseDatasetFile()
        self.assertEqual(len(dataset), 3)
        self.assertIn('Header', dataset[0])
        self.assertIn('Value1', dataset[1])
        self.assertIn('Data1', dataset[1])
        self.assertIn('Value2', dataset[2])
        self.assertIn('Data2', dataset[2])
        
        mock_read_excel.assert_called_once_with(DATASET_PATH)
    
    @patch('pandas.read_excel')
    @patch('logging.info')
    def testEmptyRowHandling(self, mock_logging, mock_read_excel):
        mock_df = pandas.DataFrame({
            'Column1': ['Header', 'Value1', '', 'Value3'],
            'Column2': ['Header', 'Data1', '', 'Data3'],
            'Column3': ['Header', 'Info1', '', 'Info3'],
            'Column4': ['Header', 'Info1', '', 'Info3'],
            'Column5': ['Header', 'Info1', '', 'Info3'],
            'Column6': ['Header', 'Info1', '', 'Info3'],
            'Column7': ['Header', 'Info1', '', 'Info3'],
            'Column8': ['Header', 'Info1', '', 'Info3'],
            'Column9': ['Header', 'Info1', '', 'Info3'],
            'Column10': ['Header', 'Info1', '', 'Info3']
        })
        mock_read_excel.return_value = mock_df
        with patch('compiler.helpers.dataset.checkRowEmpty', side_effect=[False, False, True, False]):
            parseDatasetFile()

        self.assertEqual(len(dataset), 3)
        self.assertIn('Header', dataset[0])
        self.assertIn('Value1', dataset[1])
        mock_logging.assert_called_with("Removed empty row: ['', '', '', '', '', '', '', '', '', '']")

    
    @patch('pandas.read_excel', side_effect=FileNotFoundError("File not found"))
    def testFileNotFoundError(self, mock_read_excel):
        with self.assertRaises(FileNotFoundError):
            parseDatasetFile()
    
    @patch('pandas.read_excel', side_effect=Exception("Invalid Excel file"))
    def testOtherExceptions(self, mock_read_excel):
        with self.assertRaises(Exception) as context:
            parseDatasetFile()
        self.assertIn("Invalid Excel file", str(context.exception))

if __name__ == '__main__':
    unittest.main()