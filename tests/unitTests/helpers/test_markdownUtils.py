import unittest, re, pathlib as Path
from unittest.mock import patch
from compiler.helpers.markdownUtils import (
    checkForDoubleBoldInText, checkForBoldInTitle, 
    checkForDoublePageFrontmatter, findWIPItems, extractPageFrontmatters, generateTags, 
    ERROR_DOUBLE_PAGE_FRONTMATTER, ERROR_NO_TAXCO_FOUND, ERROR_INVALID_TAXCO,
)

class TestGeneratingTags(unittest.TestCase):
    """
    Testcases for generating tags
    """
    def setUp(self):
        self.filePath = "dummy_path.txt"

    def testTaxonomieNone(self):
        tags, errors = generateTags([], None, self.filePath)
        self.assertIn(ERROR_NO_TAXCO_FOUND, errors[0])
    
    def testTaxonomieListNone(self):
        tags, errors = generateTags(['None'], None, self.filePath)
        self.assertIn(ERROR_NO_TAXCO_FOUND, errors[0])
    
    def testTaxonomieListQuoute(self):
        tags, errors = generateTags([''], None, self.filePath)
        self.assertIn(ERROR_NO_TAXCO_FOUND, errors[0])
    
    def testTaxonomieListEmpty(self):
        tags, errors = generateTags([], None, self.filePath)
        self.assertIn(ERROR_NO_TAXCO_FOUND, errors[0])
    
    def testTaxonomieListWithWrongRegex(self):
        tags, errors = generateTags(['ib-19.2.2.2.OI'], None, self.filePath)
        self.assertIn((f"{ERROR_INVALID_TAXCO} `ib-19.2.2.2.OI`"), errors[0])
    
    @patch("compiler.helpers.markdownUtils.splitTaxonomie", return_value=('ib-19', '2', 'Anders-Eerste-Onderdeel', 'OI'))
    def testTaxonomieListWithWrongAndRightRegex(self, _):
        tags, errors = generateTags(['ib-19.2.3.1.Test.JA', 'ib-19.2.Ander-Eerste-Onderdeel.OI'], None, self.filePath)
        self.assertIn((f"{ERROR_INVALID_TAXCO} `ib-19.2.3.1.Test.JA`"), errors[0])
        self.assertIn("Implementatieproces", tags)
        self.assertIn("Bouwen softwaresysteem", tags)
        self.assertIn("HBO-i/niveau-2", tags)
        self.assertIn("Ander-Eerste-Onderdeel", tags)
    
    def testtc1NotInDataset(self):
        return
    
    def testtc1InDataset(self):
        return
    
    def testRowTc3NotInDataset(self):
        return
    
    def testRowTc3InDataset(self):
        return
    
    def testTc3NotInDataset(self):
        return
    
    def testTc3InDataset(self):
        return
    
    def testDoubleHBOiLevel(self):
        return
    
    def testProcesColNotInDataset(self):
        return
    
    def testProcesColInDataset(self):
        return
    
    def testProcesNotInTags(self):
        return
    
    def testProcesInTags(self):
        return
    
    def testProcesStapColNotInDataset(self):
        return
    
    def testProcesStapColInDataset(self):
        return
    
    def testProcesStapInTags(self):
        return
    
    def testProcesStapNotInTags(self):
        return
    
    def testTc3InTags(self):
        return
    
    def testTc3NotInTags(self):
        return
    
    def testTaxonomieNotInTaxonomieTags(self):
        return
    
    def testTaxonomoieInTaxonomieTags(self):
        return
    
    def testTaxonomieNotNeededOnLevel(self):
        return
    
    def testTaxonomieNeededOnLevel(self):
        return
    
    def testTagsListEmptyWithErrors(self):
        return
    
    def testTagsListEmptyWithoutErrors(self):
        return
    
    def testTagsListNotEmptyWithErrors(self):
        return
    
    def testTagsListNotEmptyWithoutErrors(self):
        return
    
    def testExistingTagsListEmpty(self):
        return
    
    def testExistingTagsListNotEmpty(self):
        return



class TestSplitTaxonomie(unittest.TestCase):
    """
    Testcases for splitting the taxonomie codes
    """
    """
    tc1
        1 letter
        geen streepje
        geen cijfer
        spliten met punt
        spatie
    tc2
        0
        2
        4
        -1
    tc3
        Spaties
    """

class TestExtractingHeaderValues(unittest.TestCase):
    """
    Testcases for extracting header values
    """
    def testSingleHeaderValue(self):
        content = "title: My Document\ndraft: true"
        self.assertEqual(extractPageFrontmatters(content, "draft"), ["true"])

    def testMissingHeaderValue(self):
        content = "title: My Document\ndraft: true"
        self.assertIsNone(extractPageFrontmatters(content, "tags"))

    def testEmptyField(self):
        content = "title: My Document\ndraft:"
        self.assertIsNone(extractPageFrontmatters(content, "author"))

    def testListValues(self):
        content = """tags:\n  - python\n  - unittest\n  - regex"""
        self.assertEqual(extractPageFrontmatters(content, "tags"), ["python", "unittest", "regex"])

    def test_mixed_format(self):
        content = """title: Sample Doc\ntags:\n  - python\n  - unittest"""
        self.assertEqual(extractPageFrontmatters(content, "tags"), ["python", "unittest"])
        self.assertEqual(extractPageFrontmatters(content, "title"), ["Sample Doc"])

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
