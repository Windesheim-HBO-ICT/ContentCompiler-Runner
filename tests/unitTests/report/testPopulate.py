import unittest
from compiler.config import NOT_NECESSARY_ICON
from compiler.report.populate import (
    processColumn, addNewTaxcoReportEntry, updateTaxcoReport, populateTaxcoReport,
    taxcoReport, contentReport
)

class TestPopulateTaxcoReport(unittest.TestCase):
    """
    Testcases for populateTaxcoreport
    """

class TestUpdateTaxcoReport(unittest.TestCase):
    """
    Testcases for updateTaxcoReport
    """

class TestAddingNewTaxcoReportEntry(unittest.TestCase):
    """
    Testcases for addNewTaxcoReportEntry
    """

class TestPopulateContentReport(unittest.TestCase):
    """
    Testcases for populateContentReport
    """

class TestProcessColumn(unittest.TestCase):
    """
    Testcasees for processColumn
    """
    def testSingleX(self):
        self.assertEqual(processColumn("X"), [NOT_NECESSARY_ICON])
    
    def testSingleOthers(self):
        self.assertEqual(processColumn("A"), ['x'])
    
    def testMultipleValues(self):
        self.assertEqual(processColumn("X,A,B,X"), [NOT_NECESSARY_ICON, 'x', 'x', NOT_NECESSARY_ICON])
    
    def testMixed(self):
        self.assertEqual(processColumn("x,X,x"), ['x', NOT_NECESSARY_ICON, 'x'])


if __name__ == '__main__':
    unittest.main()