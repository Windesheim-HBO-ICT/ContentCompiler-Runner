import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from compiler.helpers.parseContent import appendFileToSpecificList, saveParsedFile
from compiler.config import (
    failedFiles, ignoredFiles, parsedFiles, WIPFiles,
    SUCCESS_ICON, TODO_ITEMS_ICON, WARNING_ICON, FAIL_CROSS_ICON,
    FILE_HAS_IGNORE_TAG, ERROR_NO_TAXCO_FOUND, ERROR_TAXCO_NOT_NEEDED,
    ERROR_INVALID_TAXCO
)

# Tests error: File path relative
class TestParseMarkdownFiles(unittest.TestCase):
    """
    Testcases for parseMarkdownFiles
    """

class TestValidateContent(unittest.TestCase):

    """
    Testcases for validateContent
    """

class TestAppendFile(unittest.TestCase):
    """
    Testcases for appendFile for specific list
    """

class TestSaveParsedFile(unittest.TestCase):
    def setUp(self):
        self.filePath = Path("test/path/to/test_file.md")
        self.taxonomie = ["taxo-1", "taxo-2"]
        self.tags = ["tag1", "tag2", "tag3"]
        self.difficulty = ["Medium"]
        self.destFilePath = Path("dest/path/to/test_file.md")
        self.content = "---\nold frontmatter\n---\n\n# Content Title\n\nThis is the body content."

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_basic_frontmatter_creation(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            self.tags, 
            None,  # No difficulty
            False,  # Not a draft
            False,  # No ignore tag
            self.content, 
            self.destFilePath
        )
        
        mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        mock_file.assert_called_once_with(self.destFilePath, 'w', encoding='utf-8')
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertIn(f"title: {self.filePath.stem}", written_content)
        self.assertIn(f"taxonomie: {self.taxonomie}", written_content)
        
        for tag in self.tags:
            self.assertIn(f"- {tag}", written_content)
        
        self.assertNotIn("difficulty:", written_content)
        self.assertNotIn("draft:", written_content)
        self.assertNotIn("ignore:", written_content)
        
        self.assertIn("# Content Title", written_content)
        self.assertIn("This is the body content.", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_with_all_optional_fields(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            self.tags, 
            self.difficulty,
            True,  # Is a draft
            True,  # Has ignore tag
            self.content, 
            self.destFilePath
        )
        
        mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertIn("difficulty: Medium", written_content)
        self.assertIn("draft: true", written_content)
        self.assertIn("ignore: true", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_with_only_difficulty(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            self.tags, 
            self.difficulty,
            False,  # Not a draft
            False,  # No ignore tag
            self.content, 
            self.destFilePath
        )
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertIn("difficulty: Medium", written_content)
        self.assertNotIn("draft:", written_content)
        self.assertNotIn("ignore:", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_with_only_draft(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            self.tags, 
            None,  # No difficulty
            True,  # Is a draft
            False,  # No ignore tag
            self.content, 
            self.destFilePath
        )
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertNotIn("difficulty:", written_content)
        self.assertIn("draft: true", written_content)
        self.assertNotIn("ignore:", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_with_only_ignore(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            self.tags, 
            None,  # No difficulty
            False,  # Not a draft
            True,  # Has ignore tag
            self.content, 
            self.destFilePath
        )
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertNotIn("difficulty:", written_content)
        self.assertNotIn("draft:", written_content)
        self.assertIn("ignore: true", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_empty_tags_list(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            [],  # Empty tags list
            None, 
            False, 
            False, 
            self.content, 
            self.destFilePath
        )
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertIn("tags:", written_content)
        self.assertNotIn("- ", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_empty_taxonomie_list(self, mock_file, mock_parent):
        saveParsedFile(
            self.filePath, 
            [],  # Empty taxonomie list
            self.tags, 
            None, 
            False, 
            False, 
            self.content, 
            self.destFilePath
        )
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertIn("taxonomie: []", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", new_callable=mock_open)
    def test_content_without_frontmatter(self, mock_file, mock_parent):
        content_without_frontmatter = "# Just content\n\nNo frontmatter here."
        
        saveParsedFile(
            self.filePath, 
            self.taxonomie, 
            self.tags, 
            None,
            False, 
            False, 
            content_without_frontmatter, 
            self.destFilePath
        )
        
        written_content = mock_file().write.call_args[0][0]
        
        self.assertIn("# Just content", written_content)
        self.assertIn("No frontmatter here.", written_content)

    @patch("pathlib.Path.parent")
    @patch("builtins.open", side_effect=IOError("Test file write error"))
    def test_file_write_error(self, mock_file, mock_parent):
        with self.assertRaises(IOError):
            saveParsedFile(
                self.filePath, 
                self.taxonomie, 
                self.tags, 
                None,
                False, 
                False, 
                self.content, 
                self.destFilePath
            )

if __name__ == '__main__':
    unittest.main()
