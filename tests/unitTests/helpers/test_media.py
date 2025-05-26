import unittest, os
from unittest.mock import patch
from pathlib import Path
from compiler.helpers.media import isLinkValid  

class TestFillMediaList(unittest.TestCase):
    """
    Testcases for fillMediaList
    """

class TestProcessMediaLinks(unittest.TestCase):
    """
    Testcases for processMediaLinks
    """

class TestProcessMediaList(unittest.TestCase):
    """
    Testcases for processMediaList
    """

class TestProcessDynamicLinks(unittest.TestCase):
    """
    Testcases for processDynamicLinks
    """

class TestValidLinks(unittest.TestCase):
    """
    Testcases for checking if a link is valid
    """
    @patch("os.walk")
    def testLinkValidExistingFile(self, mock_walk):
        mock_walk.return_value = [("/test/src", [], ["file.pdf", "image.png"])]
        self.assertTrue(isLinkValid("/test/src/file.pdf"))
        self.assertTrue(isLinkValid("/test/src/image.png"))
        
    @patch("os.walk")
    def testIsLinkValidNonExistingFile(self, mock_walk):
        mock_walk.return_value = [("/test/src", [], ["file.pdf", "image.png"])]
        self.assertFalse(isLinkValid("/test/src/missing.doc"))
        self.assertFalse(isLinkValid("/test/src/other.png"))
        
    @patch("os.walk")
    def testIsLinkValidWithAnchor(self, mock_walk):
        mock_walk.return_value = [("/test/src", [], ["file.pdf"])]
        self.assertTrue(isLinkValid("/test/src/file.pdf#section"))
        
    @patch("os.walk")
    def testIsLinkValidWithPipe(self, mock_walk):
        mock_walk.return_value = [("/test/src", [], ["file.pdf"])]
        self.assertTrue(isLinkValid("file.pdf | Description"))


if __name__ == "__main__":
    unittest.main()