from pathlib import Path
import urllib.parse
import re, os, shutil, logging
from compiler.report.table import createMediaTableRow
from compiler.config import (
    failedMediaFiles,
    SRC_DIR, DEST_DIR,
    TODO_ITEMS_ICON,
    VALID_DYNAMIC_LINK_PREFIXES, IGNORE_FOLDERS,
    DYNAMIC_LINK_REGEX, IMAGE_REGEX, PDF_REGEX, MD_IMAGE_REGEX,
    ERROR_PDF_NOT_USED, ERROR_IMAGE_NOT_USED, ERROR_INVALID_DYNAMIC_LINK, 
    ERROR_IMAGE_NOT_FOUND, ERROR_PDF_NOT_FOUND, ERROR_PDF_FORMAT_INVALID, ALT_PDF_REGEX
)

# Global candidate list for media files (images and PDFs)
candidateMediaFiles = []

"""
Initialize the global candidateMediaFiles list by collecting all files in SRC_DIR that might be referenced (images, PDFs, etc.).
"""
def fillMediaList():
    global candidateMediaFiles
    candidateMediaFiles = []

    for root, dirs, files in os.walk(SRC_DIR):
        # Skip folders in IGNORE_FOLDERS
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]        
        # Add all files, except files with .md, .github and .gitignore to the candidate list
        for file in files:
            if not file.endswith(('.md', '.github', '.gitignore', '.gitkeep')):
                candidateMediaFiles.append(Path(root) / file)

"""
Combines dynamic link processing, image validation, and PDF validation.
Returns updated content and a list of error messages.
"""
def processMediaLinks(filePath: Path, content: str, skipValidateDynamicLinks: bool = False):
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

"""
After all markdown files have been processed, check any remaining
media files in candidateMediaFiles. They were never referenced,
so mark them as "not used" errors.
"""
def processMediaList():
    for file in candidateMediaFiles:
        if file.suffix.lower() == '.pdf':
            error = f"{ERROR_PDF_NOT_USED} `{file.name}`"
        else:
            error = f"{ERROR_IMAGE_NOT_USED} `{file.name}`"

        logging.warning(error)
        
        filePath = Path(SRC_DIR) / file
        failedMediaFiles.append(createMediaTableRow(TODO_ITEMS_ICON, file.name, filePath, error))


"""
Process dynamic links in the markdown content:
    - Removes 'content/' from links
    - Checks if link is valid (file exists) unless skipValidateDynamicLinks=True
"""
def processDynamicLinks(filePath: Path, content: str, skipValidateDynamicLinks: bool):
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

        if skipValidateDynamicLinks:
            continue


        if not isLinkValid(newLink):
            # Escape pipe characters for Markdown
            errors.append(f"{ERROR_INVALID_DYNAMIC_LINK} `{newLink.replace('|', '\|')}`")
            logging.warning(f"{ERROR_INVALID_DYNAMIC_LINK} `{newLink}` in file: {filePath}")

    return content, errors

"""
Check if a dynamic link is valid (the referenced file actually exists).
"""
def isLinkValid(dynamicLink: str) -> bool:
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
                return True

    return False

def validateImageLinks(content: str) -> list[str]:
    errors = []
    # Find wiki-style image matches
    wikiImageMatches = re.findall(IMAGE_REGEX, content)
    # Find standard Markdown image matches
    mdImageMatches = re.findall(MD_IMAGE_REGEX, content)
    # Process wiki-style image links
    for match in wikiImageMatches:
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

        if foundFile and foundFile.exists():
            try:
                relPath = foundFile.relative_to(SRC_DIR)
            except ValueError:
                relPath = foundFile.name
            destFile = DEST_DIR / relPath
            destFile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(foundFile, destFile)
            logging.info(f"Copied image '{foundFile}' -> '{destFile}'")
            candidateMediaFiles.remove(foundFile)
        else:
            errMsg = f"{ERROR_IMAGE_NOT_FOUND} `{imageName}`"
            logging.warning(errMsg)
    
    # Process standard Markdown image links
    for match in mdImageMatches:
        # match[0] is the alt text, match[1] is the image path
        imagePath = match[1].strip() if match[1] else ""

        if not imagePath:
            continue
            
        # Decode URL-encoded spaces (%20 → space)
        imagePath = urllib.parse.unquote(imagePath)
    
        # Extract just the file name from the path
        imageName = Path(imagePath).name

        # Skip remote images
        if imagePath.startswith('http://') or imagePath.startswith('https://'):
            continue

        foundFile = None
        for file in candidateMediaFiles:
            if file.name == imageName:
                foundFile = file
                break

        if foundFile and foundFile.exists():
            try:
                relPath = foundFile.relative_to(SRC_DIR)
            except ValueError:
                relPath = foundFile.name
            destFile = DEST_DIR / relPath
            destFile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(foundFile, destFile)
            logging.info(f"Copied image '{foundFile}' -> '{destFile}'")
            candidateMediaFiles.remove(foundFile)
        else:
            errMsg = f"{ERROR_IMAGE_NOT_FOUND} `{imageName}`"
            logging.warning(errMsg)
    
    return errors


"""
- Matches standard PDF links PDF_REGEX. Copies them if found, else logs error.
- Matches invalid PDF links with ALT_PDF_REGEX. These are flagged as errors.
Removes found files from candidateMediaFiles to avoid "unused" flags.
"""
def validatePdfLinks(content: str) -> list[str]:
    errors = []

    # Standard PDF links
    pdfFiles = re.findall(PDF_REGEX, content)
    
    for file in pdfFiles:
        # file[0] = [[pdf]], file[2] = markdown pdf
        pdfPath = file[0] or file[2]  
        if not pdfPath:
            continue

        # Decode URL-encoded spaces (%20 → space)
        pdfPath = urllib.parse.unquote(pdfPath)

        pdfFileName = pdfPath.strip()
        
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

    # Invalid PDF links with '!' at the front
    altPdfMatches = re.findall(ALT_PDF_REGEX, content)    
    for file in altPdfMatches:
        pdfFileName = file.strip()
        
        errMsg = f"{ERROR_PDF_FORMAT_INVALID} `{pdfFileName}`"
        logging.warning(errMsg)
        errors.append(errMsg)

    return errors
