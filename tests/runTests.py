# Imports
from pathlib import Path
import shutil, os, sys, logging, time, pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Override configuration values before any other imports
from compiler import config
config.DATASET_PATH = Path(__file__).resolve().parent / 'test_dataset.xlsx'
config.SRC_DIR = Path(__file__).resolve().parent / 'test_cases'
config.DEST_DIR = Path(__file__).resolve().parent / 'test_cases_build'
config.TAXCO_REPORT_PATH = Path(__file__).resolve().parent / 'reports/actual_taxco_test_report.md'
config.CONTENT_REPORT_PATH = Path(__file__).resolve().parent / 'reports/actual_content_test_report.md'

# Variables and functions
from compiler.config import failedFiles, WIPFiles
from compiler.helpers.parseContent import parseMarkdownFiles
from compiler.config import DATASET_PATH, SRC_DIR, DEST_DIR
from compiler.runCompiler import ContentCompiler

class TestRunner:
    def __init__(self):
        self.setupPaths()

    def setupPaths(self):
        self.EXPECTED_TAXCO_TEST_REPORT_PATH = 'tests/reports/expected_taxco_test_report.md'
        self.ACTUAL_TAXCO_TEST_REPORT_PATH = 'tests/reports/actual_taxco_test_report.md'
        self.EXPECTED_CONTENT_TEST_REPORT_PATH = 'tests/reports/expected_content_test_report.md'
        self.ACTUAL_CONTENT_TEST_REPORT_PATH = 'tests/reports/actual_content_test_report.md'

    def validateTestReport(self, expected: str, actual: str) -> bool:
        expectedTestReportPath = Path(__file__).resolve().parents[1] / expected
        actualTestReportPath = Path(__file__).resolve().parents[1] / actual
        
        with open(expectedTestReportPath, 'r', encoding='utf-8') as f1, open(actualTestReportPath, 'r', encoding='utf-8') as f2:
            expectedTestReportContent = f1.read()
            actualTestReportContent = f2.read()

        return expectedTestReportContent == actualTestReportContent
    
    def countDraftFiles(self, fileList) -> int:
        if not fileList:  
            return 0

        draftFiles = 0
        for file in fileList:
            fullPath = Path("tests/test_cases_build") / file['path']

            if not fullPath.exists(): 
                logging.error(f"Error: The file at '{fullPath}' does not exist.")
                continue 

            try:
                with fullPath.open('r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('draft:'):
                            if line.strip().split(':', 1)[1].strip().lower() == 'true':
                                draftFiles += 1
                            break 
            except Exception as e:
                logging.error(f"An error occurred while reading '{fullPath}': {e}")

        return draftFiles

    def validateDraft(self) -> bool:
        expectedAmountOfDraftFiles = len(failedFiles) + len(WIPFiles)
        actualAmountOfDraftFiles = 0
        actualAmountOfDraftFiles = self.countDraftFiles(failedFiles) + self.countDraftFiles(WIPFiles)
        return expectedAmountOfDraftFiles == actualAmountOfDraftFiles
        
    # Returns the amount of markdown files in a folder
    def checkMarkdownFilesCount(self, folderPath):
        return len(list(folderPath.glob("*.md")))

    # Evaluate the tests by using check_markdown_files_count and removing the build folder afterwards
    def evaluateTests(self):
        srcDir = Path(__file__).resolve().parents[0] / 'test_cases'
        destDir = Path(__file__).resolve().parents[0] / 'test_cases_build'
        return self.checkMarkdownFilesCount(srcDir) == self.checkMarkdownFilesCount(destDir)

    def run(self):
        try:
            # Run script
            compiler = ContentCompiler(skipLinkCheck=False)  # Adjust argument if needed
            compiler.compile()

            if not self.validateTestReport(self.EXPECTED_TAXCO_TEST_REPORT_PATH, self.ACTUAL_TAXCO_TEST_REPORT_PATH):
                logging.error("Taxco Test report validation failed")
                sys.exit(11)

            if not self.validateTestReport(self.EXPECTED_CONTENT_TEST_REPORT_PATH, self.ACTUAL_CONTENT_TEST_REPORT_PATH):
                logging.error("Content Test report validation failed")
                sys.exit(12)

            if not self.evaluateTests():
                logging.error("Test evaluation failed")
                sys.exit(13)

            if not self.validateDraft():
                logging.error("Draft test failed")
                sys.exit(14)

            logging.info("Testing completed successfully")
            sys.exit(0)
                
        except Exception as e:
            logging.error(f"Error during test execution: {str(e)}")
            raise

def main():
    try:
        runner = TestRunner()
        runner.run()
    except Exception as e:
        logging.error(f"Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()