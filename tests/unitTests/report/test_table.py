import unittest
from pathlib import Path
from compiler.report.table import (
    generateMarkdownTable
)
import compiler.config

class TestGenerateMarkdownTable(unittest.TestCase):
    """
    Testcases for generateMarkdowntable
    """
    def testGenerateMarkdownTable(self):
        headers = ["Name", "Age", "City"]
        rows = [["Anne", "30", "Zwolle"], ["Bert", "25", "Almere"]]
        expected_output = (
            "| Name | Age | City |\n"
            "| --- | --- | --- |\n"
            "| Anne | 30 | Zwolle |\n"
            "| Bert | 25 | Almere |\n"
        )
        self.assertEqual(generateMarkdownTable(headers, rows), expected_output)
    
    def testGenerateMarkdownTableEmpty(self):
        headers = []
        rows = []
        expected_output = "|  |\n|  |\n"
        self.assertEqual(generateMarkdownTable(headers, rows), expected_output)
    
    def testGenerateMarkdownTableSingleRow(self):
        headers = ["ID", "Status"]
        rows = [["1", "Completed"]]
        expected_output = (
            "| ID | Status |\n"
            "| --- | --- |\n"
            "| 1 | Completed |\n"
        )
        self.assertEqual(generateMarkdownTable(headers, rows), expected_output)

class TestCreateFileReportRow(unittest.TestCase):
    """
    Testcases for createFileReportRow
    """

class TestFormatFileReportTable(unittest.TestCase):
    """
    Testcases for formatFileReportTable
    """

class TestCreateMediaTableRow(unittest.TestCase):
    """
    Testcases for createMediaTableRow
    """

class TestFormatMediaReportTable(unittest.TestCase):
    """
    Testcases for formatMediaReportTable
    """

if __name__ == '__main__':
    unittest.main()