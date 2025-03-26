import os, time, shutil, argparse, logging
from helpers.dataset import parseDatasetFile
from helpers.parseContent import parseMarkdownFiles
from report.generateTaxcoReport import generateTaxcoReport
from report.generateContentReport import generateContentReport
from report.populate import populateTaxcoReport, populateContentReport
from helpers.media import initCandidateMediaFiles, finalizeMediaValidation
from config import DATASET_PATH, SRC_DIR, DEST_DIR

class ContentCompiler:
    def __init__(self, skipLinkCheck: bool = False):
        self.skipLinkCheck = skipLinkCheck
        self.setupLogging()

    @staticmethod
    def setupLogging() -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def handlePaths(self) -> None:
        # Check if the dataset and source directory exist
        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError(f"Dataset file {DATASET_PATH} not found.")
        if not os.path.exists(SRC_DIR):
            raise FileNotFoundError(f"Source directory {DATASET_PATH} not found.")
        
        # Create destination directory
        if os.path.exists(DEST_DIR):
            shutil.rmtree(DEST_DIR)
        os.mkdir(DEST_DIR)

    def compile(self) -> None:
        try:            
            # Handle paths checking and creation
            self.handlePaths()
            
            logging.info("Starting content compilation...")
            
            parseDatasetFile()
            logging.info("Dataset parsed successfully")
            
            populateTaxcoReport()
            populateContentReport()
            logging.info("Reports populated")
            
            initCandidateMediaFiles()
            logging.info("Candidate media files initialized")
            
            parseMarkdownFiles(self.skipLinkCheck)
            logging.info("Markdown files parsed")
            
            finalizeMediaValidation()
            logging.info("Media validation finalized")
            
            generateTaxcoReport()
            generateContentReport()
            logging.info("Reports generated successfully")
            
        except Exception as e:
            logging.error(f"Error during compilation: {str(e)}", exc_info=True)
            raise

def main() -> None:
    parser = argparse.ArgumentParser(description="Compile content script.")
    parser.add_argument('--skip-link-check', required=False, action='store_true', help='Skip link check in markdown helpers.')
    args = parser.parse_args()

    startTime = time.time()
    
    try:
        compiler = ContentCompiler(skipLinkCheck=args.skip_link_check)
        compiler.compile()
    except Exception as e:
        logging.error(f"Compilation failed: {str(e)}")
        exit(1)
    finally:
        elapsedTime = time.time() - startTime
        logging.info(f"Execution time: {elapsedTime:.2f} seconds")

if __name__ == "__main__":
    main()
