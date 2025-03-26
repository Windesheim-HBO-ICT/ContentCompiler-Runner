from pathlib import Path
import re, os, shutil, logging
from report.table import createMediaTableRow
from config import (
    failedMediaFiles,
    SRC_DIR, DEST_DIR,
    TODO_ITEMS_ICON,
    VALID_DYNAMIC_LINK_PREFIXES, IGNORE_FOLDERS,
    DYNAMIC_LINK_REGEX, IMAGE_REGEX, PDF_REGEX,
    ERROR_PDF_NOT_USED, ERROR_IMAGE_NOT_USED, ERROR_INVALID_DYNAMIC_LINK, 
    ERROR_IMAGE_NOT_FOUND, ERROR_PDF_NOT_FOUND, ERROR_PDF_FORMAT_INVALID, ALT_PDF_REGEX
)

# Global candidate list for media files (images and PDFs)
candidateMediaFiles = []

def initCandidateMediaFiles():
    """
    Initialize the global candidateMediaFiles list by collecting all files in SRC_DIR that might be referenced (images, PDFs, etc.).
    """
    global candidateMediaFiles
    candidateMediaFiles = []

    for root, dirs, files in os.walk(SRC_DIR):
        # Skip folders in IGNORE_FOLDERS
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
        
        # Add all files to the candidate list
        for file in files:
            # Ignore files with extensions like .md, .github, etc.
            if not file.endswith(('.md', '.github', '.gitignore')):
                candidateMediaFiles.append(Path(root) / file)


def processMediaLinks(filePath: Path, content: str, skipValidateDynamicLinks: bool = False):
    """
    Combines dynamic link processing, image validation, and PDF validation.
    Returns updated content and a list of error messages.
    """
    errors = []

    # 1. Process dynamic links
    content, dynErrors = processDynamicLinks(filePath, content, skipValidateDynamicLinks)
    errors.extend(dynErrors)

    # 2. Validate/copy images
    imgErrors = validateImageLinks(content)
    errors.extend(imgErrors)

    # 3. Validate/copy PDFs
    pdfErrors = validatePdfLinks(content)
    errors.extend(pdfErrors)

    return content, errors


def finalizeMediaValidation() -> None:
    """
    After all markdown files have been processed, check any remaining
    media files in candidateMediaFiles. They were never referenced,
    so mark them as "not used" errors.
    """
    global candidateMediaFiles

    for file in candidateMediaFiles:
        if file.suffix.lower() == '.pdf':
            error = f"{ERROR_PDF_NOT_USED} `{file.name}`"
        else:
            error = f"{ERROR_IMAGE_NOT_USED} `{file.name}`"

        logging.warning(error)
        
        filePath = Path(SRC_DIR) / file
        failedMediaFiles.append(createMediaTableRow(TODO_ITEMS_ICON, file.name, filePath, SRC_DIR, error))


def processDynamicLinks(filePath: Path, content: str, skipValidateDynamicLinks: bool):
    """
    Process dynamic links in the markdown content:
      - Removes 'content/' from links
      - Checks if link is valid (file exists) unless skipValidateDynamicLinks=True
    """
    dynamicLinks = re.findall(DYNAMIC_LINK_REGEX, content)
    errors = []
    
    for link in dynamicLinks:
        cleanedLink = link.strip('[[]]')

        # Skip links that start with any valid prefix
        if any(cleanedLink.startswith(prefix) for prefix in VALID_DYNAMIC_LINK_PREFIXES):
            continue

        # Remove 'content/' because in production the content is not in 'content/' but at build root
        newLink = cleanedLink.replace('content/', '')
        content = content.replace(cleanedLink, newLink)

        # If we skip validation, move on
        if skipValidateDynamicLinks:
            continue

        # Check if the link is valid
        if not isLinkValid(newLink):
            # Escape pipe characters for Markdown
            errors.append(f"{ERROR_INVALID_DYNAMIC_LINK} `{newLink.replace('|', '\|')}`")
            logging.warning(f"{ERROR_INVALID_DYNAMIC_LINK} `{newLink}` in file: {filePath}")

    return content, errors

def isLinkValid(dynamicLink: str) -> bool:
    """
    Check if a dynamic link is valid (the referenced file actually exists).
    """

    # Remove any anchor (e.g. #section)
    if '#' in dynamicLink:
        dynamicLink = dynamicLink.split('#')[0]
    
    # If there's a pipe, the actual file name is before the pipe
    linkParts = dynamicLink.split('|')
    fileName = linkParts[0].strip().split('/')[-1]

    # Search in all subdirectories
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.startswith(fileName):
                # If the file is found, the link is valid, so break the loop
                return True

    return False


def validateImageLinks(content: str) -> list[str]:
    """
    Search for image links (IMAGE_REGEX).
    If the file is found, copy it to build folder. If not, log an error.
    Removes found files from candidateMediaFiles to avoid "unused" flags.
    """
    errors = []
    imageMatches = re.findall(IMAGE_REGEX, content)

    for match in imageMatches:
        # match is a tuple from the capture groups
        # e.g. ('someImage.png', 'optionalCaption') or similar
        imageName = match[0].strip() if match[0] else ""
        if not imageName:
            continue

        # Skip remote images
        if imageName.startswith('http://') or imageName.startswith('https://'):
            continue

        foundFile = None
        for file in candidateMediaFiles:
            if file.name == imageName:
                foundFile = file
                break

        # If the file is found, copy it to build folder
        if foundFile and foundFile.exists():
            try:
                relPath = foundFile.relative_to(SRC_DIR)
            except ValueError:
                # If not relative to srcDir, just use the file name
                relPath = foundFile.name

            destFile = DEST_DIR / relPath
            destFile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(foundFile, destFile)
            logging.info(f"Copied image '{foundFile}' -> '{destFile}'")
            candidateMediaFiles.remove(foundFile)
        else:
            errMsg = f"{ERROR_IMAGE_NOT_FOUND} `{imageName}`"
            logging.warning(errMsg)
            errors.append(errMsg)

    return errors


def validatePdfLinks(content: str) -> list[str]:
    """
    - Matches standard PDF links PDF_REGEX. Copies them if found, else logs error.
    - Matches invalid PDF links with ALT_PDF_REGEX. These are flagged as errors.
    Removes found files from candidateMediaFiles to avoid "unused" flags.
    """
    errors = []

    # Standard PDF links
    pdfFiles = re.findall(PDF_REGEX, content)
        
    for file in pdfFiles:
        pdfFileName = file.strip()
        
        # Skip remote PDFs
        if pdfFileName.startswith('http://') or pdfFileName.startswith('https://'):
            continue

        foundFile = None
        for file in candidateMediaFiles:
            if file.name == pdfFileName:
                foundFile = file
                break

        # If the file is found, copy it to build folder
        if foundFile and foundFile.exists():
            try:
                relPath = foundFile.relative_to(SRC_DIR)
            except ValueError:
                relPath = foundFile.name

            destFile = DEST_DIR / relPath
            destFile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(foundFile, destFile)
            logging.info(f"Copied PDF '{foundFile}' -> '{destFile}'")
            candidateMediaFiles.remove(foundFile)
        else:
            errMsg = f"{ERROR_PDF_NOT_FOUND} `{pdfFileName}`"
            logging.warning(errMsg)
            errors.append(errMsg)

    # Invalid PDF links with '!'
    altPdfMatches = re.findall(ALT_PDF_REGEX, content)    
    for file in altPdfMatches:
        pdfFileName = file.strip()
        
        errMsg = f"{ERROR_PDF_FORMAT_INVALID} `{pdfFileName}`"
        logging.warning(errMsg)
        errors.append(errMsg)

    return errors
