import os, time, shutil, argparse, logging
from helpers.dataset import parseDatasetFile
from helpers.parseContent import parseMarkdownFiles
from report.generateTaxcoReport import generateTaxcoReport
from report.generateContentReport import generateContentReport
from report.populate import populateTaxcoReport, populateContentReport
from helpers.media import initCandidateMediaFiles, finalizeMediaValidation
from config import DEST_DIR, SRC_DIR, TAXCO_REPORT_PATH, CONTENT_REPORT_PATH, DATASET

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
        
    def handlePaths(self, dataset, srcDir, destDir) -> None:
        # Check if the dataset and source directory exist
        if not os.path.exists(dataset):
            raise FileNotFoundError(f"Dataset file {dataset} not found.")
        if not os.path.exists(srcDir):
            raise FileNotFoundError(f"Source directory {srcDir} not found.")
        
        # Create destination directory
        if os.path.exists(destDir):
            shutil.rmtree(destDir)
        os.mkdir(destDir)

    def compile(self) -> None:
        try:
            dataset = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', DATASET))
            srcDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', SRC_DIR))
            destDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', DEST_DIR))
            taxcoReportPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', TAXCO_REPORT_PATH))
            contentReportPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', CONTENT_REPORT_PATH))
            
            # Handle paths checking and creation
            self.handlePaths(dataset, srcDir, destDir)
            
            logging.info("Starting content compilation...")
            
            parseDatasetFile(dataset)
            logging.info("Dataset parsed successfully")
            
            populateTaxcoReport()
            populateContentReport()
            logging.info("Reports populated")
            
            initCandidateMediaFiles(srcDir)
            logging.info("Candidate media files initialized")
            
            parseMarkdownFiles(srcDir, destDir, self.skipLinkCheck)
            logging.info("Markdown files parsed")
            
            finalizeMediaValidation()
            logging.info("Media validation finalized")
            
            generateTaxcoReport(taxcoReportPath)
            generateContentReport(contentReportPath)
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
