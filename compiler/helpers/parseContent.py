import logging
from pathlib import Path
from compiler.config import (
	SRC_DIR, DEST_DIR,
    failedFiles, ignoredFiles, parsedFiles, WIPFiles,
	SUCCESS_ICON, TODO_ITEMS_ICON, WARNING_ICON,
    FILE_HAS_IGNORE_TAG, ERROR_INVALID_MD_BOLD_TEXT, ERROR_NONE_IN_TAGS, ERROR_INVALID_TAXCO,
    ERROR_INVALID_MD_TITLES, ERROR_NO_TAXCO_FOUND, ERROR_TAXCO_NOT_NEEDED,
    ERROR_TITLE_NOT_EQUAL_TO_FILENAME, ERROR_WIP_FOUND, FAIL_CROSS_ICON, IGNORE_FOLDERS,
)
from compiler.helpers.media import processMediaLinks
from compiler.report.table import createFileReportRow
from compiler.helpers.markdownUtils import (
    checkForBoldInTitle, checkForDoubleBoldInText, checkForDoublePageFrontmatter,
    isFileNameAndTitleEqual, extractPageFrontmatters, findWIPItems, generateTags, checkForIgnoreTag
)


"""Update markdown files in the source directory"""
def parseMarkdownFiles(skipValidateDynamicLinks):
	for filePath in Path(SRC_DIR).rglob('*.md'):
		if shouldSkipFile(filePath):
			logging.info(f"Skipping folder: {filePath}")
			continue
		destFilePath = computeDestFilePath(filePath)
  
		content = readFileContent(filePath)
		existingTags = extractPageFrontmatters(content, 'tags')
		difficulty = extractPageFrontmatters(content, 'difficulty')
  
		errors = checkForDoublePageFrontmatter(filePath, content)

		# Check for tags that are not allowed
		if existingTags and 'None' in existingTags:
			errors.append(ERROR_NONE_IN_TAGS)
  
		updatedContent, mediaErrors = processMediaLinks(filePath, content, skipValidateDynamicLinks)
		errors.extend(mediaErrors)
  
		hasIgnoreTag = checkForIgnoreTag(filePath, updatedContent)
  
		if not hasIgnoreTag:
			taxonomie, newTags, tagErrors = processTags(filePath, updatedContent, existingTags)
			errors.extend(tagErrors)

			# Validate content (WIP items, title matching, markdown formatting)
			validationErrors, todoItems = validateContent(filePath, updatedContent)
			errors.extend(validationErrors)
		else:
			taxonomie, newTags, todoItems = [], [], []
			errors.append(FILE_HAS_IGNORE_TAG)

		# If there are any errors, the file is considered a draft unless the ignore tag is used	
		# Temporarily disabled on request from Ernst
		# isDraft = True if errors and not hasIgnoreTag else False 
		isDraft = False 
		
		appendFileToSpecificList(errors, todoItems, filePath, taxonomie, newTags)
		saveParsedFile(filePath, taxonomie, newTags, difficulty, isDraft, hasIgnoreTag, updatedContent, destFilePath)

"""Helper function to determine if a file should be skipped"""
def shouldSkipFile(filePath):
    return any(folder in str(filePath) for folder in IGNORE_FOLDERS)

"""Helper function to compute the destination file path"""
def computeDestFilePath(filePath):
    relativePath = filePath.relative_to(SRC_DIR)
    return DEST_DIR / relativePath

"""Helper function to read the content of a file"""
def readFileContent(filePath):
    with open(filePath, 'r', encoding='utf-8') as f:
        return f.read()

"""Helper function to process the tags of a markdown file"""
def processTags(filePath, content, existingTags):
    taxonomie = extractPageFrontmatters(content, 'taxonomie')
    newTags, tagErrors = generateTags(taxonomie, existingTags, filePath)
    return taxonomie, newTags, tagErrors

"""Helper function to validate the content of a markdown file"""
def validateContent(filePath, content):
	errors = []
	todoItems = findWIPItems(content)
	fileNameAndTitleEqual = isFileNameAndTitleEqual(filePath, content)
	invalidMDTitle = checkForBoldInTitle(content)
	invalidMDText = checkForDoubleBoldInText(content)

	if todoItems:
		errors.append(f"{ERROR_WIP_FOUND}<br>{'<br>'.join(todoItems)}")

	if not fileNameAndTitleEqual:
		title = extractPageFrontmatters(content, 'title')

		if isinstance(title, list):
			title = title[0] if title else ""

		logging.warning(f"Titel '{title}' komt niet overeen met bestandsnaam '{filePath.stem}' in bestand: '{filePath}'")
		errors.append(ERROR_TITLE_NOT_EQUAL_TO_FILENAME)
		errors.append(f"- Titel: {title}")
		errors.append(f"- Bestandsnaam: {filePath.stem}")

	if invalidMDTitle:
		title = extractPageFrontmatters(content, 'title')
		logging.warning(f"Titel '{invalidMDTitle}' is/zijn verkeerd opgemaakt in bestand: '{filePath}'")
		errors.append(ERROR_INVALID_MD_TITLES)
		errors.extend([f"- {error.replace('**', '\\*\\*')}" for error in invalidMDTitle])

	if invalidMDText:
		logging.warning(f"Tekst is verkeerd opgemaakt in bestand: '{filePath}'")
		errors.append(ERROR_INVALID_MD_BOLD_TEXT)
		errors.extend([f"- {error.replace('**', '\\*\\*')}" for error in invalidMDText])

	return errors, todoItems

"""Fill the different lists used for the report"""
def appendFileToSpecificList(errors, todoItems, filePath, taxonomie, tags):
	if errors:
		if FILE_HAS_IGNORE_TAG in errors:
			icon = WARNING_ICON
			targetList = ignoredFiles
		elif ERROR_NO_TAXCO_FOUND in errors or ERROR_TAXCO_NOT_NEEDED in errors:
			icon = FAIL_CROSS_ICON
			targetList = failedFiles
		elif any(error.startswith(ERROR_INVALID_TAXCO) for error in errors):
			icon = WARNING_ICON
			targetList = failedFiles
		elif todoItems:
			icon = TODO_ITEMS_ICON
			targetList = WIPFiles
		else:
			icon = WARNING_ICON
			targetList = failedFiles
	else:
		icon = SUCCESS_ICON
		targetList = parsedFiles

	targetList.append(createFileReportRow(icon, filePath, taxonomie, tags, errors))

"""Combines everything into a new md file"""
def saveParsedFile(filePath, taxonomie, tags, difficulty, isDraft, hasIgnoreTag, content, destFilePath):
    newContent = (
        f"---\ntitle: {filePath.stem}\ntaxonomie: {taxonomie}\ntags:\n" +
        '\n'.join([f"- {tag}" for tag in tags]) +
        "\n"
    )

    if difficulty:
        newContent += "difficulty: " + ''.join([f"{level}" for level in difficulty]) + "\n"
        
    if isDraft:
        newContent += "draft: true \n"
        
    if hasIgnoreTag:
        newContent += "ignore: true \n"

    newContent += "---" + content.split('---', 2)[-1]

    destFilePath.parent.mkdir(parents=True, exist_ok=True)

    with open(destFilePath, 'w', encoding='utf-8') as f:
        f.write(newContent)
