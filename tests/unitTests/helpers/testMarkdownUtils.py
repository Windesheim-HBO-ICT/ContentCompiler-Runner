import unittest, re
from unittest.mock import patch
from compiler.helpers.markdownUtils import (
    checkForDoubleBoldInText, checkForBoldInTitle, 
    checkForDoublePageFrontmatter, findWIPItems, extractHeaderValues,
    ERROR_DOUBLE_PAGE_FRONTMATTER
)

class TestMarkdownUtils(unittest.TestCase):
    """
    Testcases for generating tags
    """

    """
    Testcases for extracting header values
    """
    
class TestExtractingHeaderValues(unittest.TestCase):
    def testSingleHeaderValue(self):
        content = "title: My Document\ndraft: true"
        self.assertEqual(extractHeaderValues(content, "draft"), ["true"])

    def testMissingHeaderValue(self):
        content = "title: My Document\ndraft: true"
        self.assertIsNone(extractHeaderValues(content, "tags"))

    def testEmptyField(self):
        content = "title: My Document\ndraft:"
        self.assertIsNone(extractHeaderValues(content, "author"))

    def testListValues(self):
        content = """tags:\n  - python\n  - unittest\n  - regex"""
        self.assertEqual(extractHeaderValues(content, "tags"), ["python", "unittest", "regex"])

    def test_mixed_format(self):
        content = """title: Sample Doc\ntags:\n  - python\n  - unittest"""
        self.assertEqual(extractHeaderValues(content, "tags"), ["python", "unittest"])
        self.assertEqual(extractHeaderValues(content, "title"), ["Sample Doc"])

class TestFindingWIPFiles(unittest.TestCase):
    """
    Testcases for finding WIP items
    """
    def testFindMultipleWIPItems(self):
        content = "Some text -=TODO=- more text -=FIX=- and -=WIP=-"
        expected_items = ["-=TODO=-", "-=FIX=-", "-=WIP=-"]
        
        result = findWIPItems(content)
        self.assertEqual(result, expected_items)

    def testNoWIPItems(self):
        content = "This text has no WIP markers."
        
        result = findWIPItems(content)
        self.assertEqual(result, [])

    def testWIPItemsWithSpaces(self):
        content = "Start -=IN PROGRESS=- middle -=REVIEW=- end."
        expected_items = ["-=REVIEW=-"]
        
        result = findWIPItems(content)
        self.assertEqual(result, expected_items)

class TestBoldTextsInTitle(unittest.TestCase):
    """
    Testcases for checking if titles contain bold texts
    """
    def testValidTitlesWithoutBoldTexts(self):
        content = "# Valid Title\n\n## Another Valid Title"
        invalid_titles = checkForBoldInTitle(content)
        self.assertEqual(invalid_titles, [])

    def testTitleWIthBoldText(self):
        content = "# **Bold Title**"
        invalid_titles = checkForBoldInTitle(content)
        self.assertEqual(invalid_titles, ["**Bold Title**"])

    def testMultipleTitlesWithBoldTexts(self):
        content = "# **Bold Title**\n\n## Another **Bold** Title\n\n### Valid Title"
        invalid_titles = checkForBoldInTitle(content)
        self.assertEqual(invalid_titles, ["**Bold Title**", "Another **Bold** Title"])

    def testNoTitleFound(self):
        content = "This is just some text with **bold** words, but no titles."
        invalid_titles = checkForBoldInTitle(content)
        self.assertEqual(invalid_titles, [])

class TestDoubleBoldTexts(unittest.TestCase):
    """
    Testcases for the double bold texts
    """
    def testNormalText(self):
        # Test content with no double bold text
        content = "This is a sample text without any double bold."
        result = checkForDoubleBoldInText(content)
        self.assertEqual(result, [])

    def testNormalBold(self):
        # Test content with one double bold text
        content = "This is a **bold** text."
        result = checkForDoubleBoldInText(content)
        self.assertEqual(result, [])

    def testDoubleBold(self):
        # Test content with one double bold text
        content = "This is a ****double bold**** text."
        result = checkForDoubleBoldInText(content)
        self.assertEqual(result, ["****double bold****"])
    
    def testMultipleDoubleBold(self):
        # Test content with one double bold text
        content = "This is a ****double**** ****bold**** text."
        result = checkForDoubleBoldInText(content)
        self.assertEqual(result, ["****double****", "****bold****"])

class TestDoublePageFrontMatter(unittest.TestCase):
    """
    Testcases for the double page frontmatter
    """
    def testValidFrontmatter(self):
        content = """---\ntitle: Page Title\ntags:\n---"""
        errors = checkForDoublePageFrontmatter("test.md", content)
        self.assertEqual(errors, [])

    @patch("logging.warning")
    def testDuplicateFrontmatter(self, mock_logging):
        content = """---\ntitle: Page Title\ntags:\ntags: \n  - test\n---"""
        errors = checkForDoublePageFrontmatter("test.md", content)
        self.assertIn(f"{ERROR_DOUBLE_PAGE_FRONTMATTER}'tags'", errors)
        mock_logging.assert_called_with(f"{ERROR_DOUBLE_PAGE_FRONTMATTER}'tags'")

    def testNoFrontmatter(self):
        content = """This is a normal text file with no frontmatter."""
        errors = checkForDoublePageFrontmatter("test.md", content)
        self.assertEqual(errors, [])

    @patch("logging.warning")
    def testMultipleDuplicateFrontmatters(self, mock_logging):
        content = """---\ntitle: Page Title\ntags:\ntags: \n  - test\ntitle: Double title\n---"""
        errors = checkForDoublePageFrontmatter("test.md", content)

        match = re.search(r"'(.*?)'", errors[0])
        if match:
            actual_keys = set(match.group(1).split(", "))
        self.assertEqual({"tags", "title"}, actual_keys)

if __name__ == '__main__':
    unittest.main()
