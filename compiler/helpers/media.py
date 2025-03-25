import re
import os
import shutil
import logging
from pathlib import Path

from config import (
    SRC_DIR,
    VALID_DYNAMIC_LINK_PREFIXES, ERROR_INVALID_DYNAMIC_LINK, DYNAMIC_LINK_REGEX,
    IMAGE_REGEX, PDF_REGEX,
    ERROR_IMAGE_NOT_FOUND, ERROR_IMAGE_NOT_USED,
    ERROR_PDF_NOT_FOUND, ERROR_PDF_NOT_USED, ALT_PDF_REGEX,
    failedMediaFiles
)

# Global candidate list for media files (images and PDFs)
candidateMediaFiles = []

def initCandidateMediaFiles(srcDir: str) -> None:
    """
    Initialize the global candidateMediaFiles list by collecting all files in srcDir that might be referenced (images, PDFs, etc.).
    """
    global candidateMediaFiles
    candidateMediaFiles = []
    srcPath = Path(srcDir).resolve()

    for root, dirs, files in os.walk(srcPath):
        for file in files:
            # Ignore files with extensions like .md, .github, etc.
            if not file.endswith(('.md', '.github', '.gitignore')):
                candidateMediaFiles.append(Path(root) / file)


def processMediaLinks(filePath: Path, content: str, srcDir: str, destDir: str,skipValidateDynamicLinks: bool = False):
    """
    Combines dynamic link processing, image validation, and PDF validation.
    Returns updated content and a list of error messages.
    """
    errors = []

    # 1. Process dynamic links
    content, dynErrors = processDynamicLinks(filePath, content, srcDir, skipValidateDynamicLinks)
    errors.extend(dynErrors)

    # 2. Validate/copy images
    imgErrors = validateImageLinks(content, srcDir, destDir)
    errors.extend(imgErrors)

    # 3. Validate/copy PDFs
    pdfErrors = validatePdfLinks(content, srcDir, destDir)
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
            msg = f"{ERROR_PDF_NOT_USED} `{file.name}`"
        else:
            msg = f"{ERROR_IMAGE_NOT_USED} `{file.name}`"
        logging.warning(msg)
        failedMediaFiles.append(msg)

    # Clear the list
    candidateMediaFiles = []


def processDynamicLinks(filePath: Path, content: str, srcDir: str, skipValidateDynamicLinks: bool):
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
        if not isLinkValid(newLink, srcDir):
            # Escape pipe characters for Markdown
            errors.append(f"{ERROR_INVALID_DYNAMIC_LINK} `{newLink.replace('|', '\|')}`")
            logging.warning(f"{ERROR_INVALID_DYNAMIC_LINK} `{newLink}` in file: {filePath}")

    return content, errors

def isLinkValid(dynamicLink: str, srcDir: str) -> bool:
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
    for root, dirs, files in os.walk(srcDir):
        for file in files:
            if file.startswith(fileName):
                # If the file is found, the link is valid, so break the loop
                return True

    return False


def validateImageLinks(content: str, srcDir: str, destDir: str) -> list[str]:
    """
    Search for image links (IMAGE_REGEX).
    If the file is found, copy it to build folder. If not, log an error.
    Removes found files from candidateMediaFiles to avoid "unused" flags.
    """
    errors = []
    imageMatches = re.findall(IMAGE_REGEX, content)

    srcPath = Path(srcDir).resolve()
    destPath = Path(destDir).resolve()

    global candidateMediaFiles

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
                relPath = foundFile.relative_to(srcPath)
            except ValueError:
                # If not relative to srcDir, just use the file name
                relPath = foundFile.name

            destFile = destPath / relPath
            destFile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(foundFile, destFile)
            logging.info(f"Copied image '{foundFile}' -> '{destFile}'")
            candidateMediaFiles.remove(foundFile)
        else:
            errMsg = f"{ERROR_IMAGE_NOT_FOUND} `{imageName}`"
            logging.warning(errMsg)
            errors.append(errMsg)

    return errors


def validatePdfLinks(content: str, srcDir: str, destDir: str) -> list[str]:
    """
    - Matches standard PDF links PDF_REGEX. Copies them if found, else logs error.
    - Matches invalid PDF links with ALT_PDF_REGEX. These are flagged as errors.
    Removes found files from candidateMediaFiles to avoid "unused" flags.
    """
    errors = []
    srcPath = Path(srcDir).resolve()
    destPath = Path(destDir).resolve()

    global candidateMediaFiles

    # Standard PDF links
    pdfMatches = re.findall(PDF_REGEX, content)
    for match in pdfMatches:
        # match is e.g. ('Some text', 'doc.pdf')
        pdfFileName = match[1].strip()
        
        # Skip remote PDFs
        if pdfFileName.startswith('http://') or pdfFileName.startswith('https://'):
            continue

        foundFile = None
        for f in candidateMediaFiles:
            if f.name == pdfFileName:
                foundFile = f
                break

        # If the file is found, copy it to build folder
        if foundFile and foundFile.exists():
            try:
                relPath = foundFile.relative_to(srcPath)
            except ValueError:
                relPath = foundFile.name

            destFile = destPath / relPath
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
    for match in altPdfMatches:
        pdfFileName = match[1].strip()
        errMsg = f"Invalid PDF link with '!': `{pdfFileName}`"
        logging.warning(errMsg)
        errors.append(errMsg)

    return errors
