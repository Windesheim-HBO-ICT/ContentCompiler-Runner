import logging
from pathlib import Path
from config import (
	SRC_DIR, DEST_DIR,
    failedFiles, ignoredFiles, parsedFiles, WIPFiles,
	SUCCESS_ICON, TODO_ITEMS_ICON, WARNING_ICON,
    ERROR_DOUBLE_PAGE_FRONTMATTER, ERROR_IGNORE_TAG_USED, ERROR_INVALID_MD_BOLD_TEXT,
    ERROR_INVALID_MD_TITELS, ERROR_NO_TAXCO_FOUND, ERROR_TAXCO_NOT_NEEDED,
    ERROR_TITEL_NOT_EQUAL_TO_FILENAME, ERROR_WIP_FOUND, FAIL_CROSS_ICON, IGNORE_FOLDERS,
)
from helpers.media import processMediaLinks
from report.table import createFileReportRow
from helpers.markdownUtils import (
    checkForBoldInTitel, checkForDoubleBoldInText, checkForDoublePageFrontmatter,
    compareFileNameAndTitel, extractHeaderValues, findWIPItems, generateTags, hasIgnoreTag
)


# Update markdown files in the source directory
def parseMarkdownFiles(skipValidateDynamicLinks):
	# Loop through all markdown files in the source directory
	for filePath in Path(SRC_DIR).rglob('*.md'):
		# Determine the destination path where the new markdown file will be saved
		relativePath = filePath.relative_to(SRC_DIR)
		destFilePath = DEST_DIR / relativePath
  
		errors = []
		tagErrors = []
		todoItems = []
		taxonomie = []
		newTags = []
		isDraft = False
		isIgnore = False

        # Skip certain folders
		if any(folder in str(filePath) for folder in IGNORE_FOLDERS):
			logging.info(f"Skipping folder: {filePath}")
			continue

		# Read the content of the file
		with open(filePath, 'r', encoding='utf-8') as f:
			content = f.read()

		# Parse the file
		existingTags = extractHeaderValues(content, 'tags')
		difficulty = extractHeaderValues(content, 'difficulty')
		doublePageFrontmatter = checkForDoublePageFrontmatter(content)
		content, mediaErrors = processMediaLinks(filePath, content, skipValidateDynamicLinks)

		if doublePageFrontmatter:
			logging.warning(f"Meerdere pagina frontmatters gevonden in bestand: {filePath}")
			for error in doublePageFrontmatter:
				logging.warning(f"{error}")
			errors.append(ERROR_DOUBLE_PAGE_FRONTMATTER)
			errors.extend(doublePageFrontmatter)

		# Check if the file has an ignore tag
		if hasIgnoreTag(filePath, content):
			isIgnore = True
			errors.append(ERROR_IGNORE_TAG_USED)
		else:
			taxonomie = extractHeaderValues(content, 'taxonomie')
			newTags, tagErrors = generateTags(taxonomie, existingTags, filePath)
			todoItems = findWIPItems(content)
			fileNameAndTitelEqual = compareFileNameAndTitel(filePath, content)
			invalidMDTitels = checkForBoldInTitel(content)
			invalidMDText = checkForDoubleBoldInText(content)

			if todoItems:
				errors.append(f"{ERROR_WIP_FOUND}<br>{'<br>'.join(todoItems)}")

			if not fileNameAndTitelEqual:
				titel = extractHeaderValues(content, 'title')
				logging.warning(f"Titel '{titel}' komt niet overeen met bestandsnaam '{filePath.stem}' in bestand: '{filePath}'")
				errors.append(ERROR_TITEL_NOT_EQUAL_TO_FILENAME)
				errors.append(f"- Titel: {titel}")
				errors.append(f"- Bestandsnaam: {filePath.stem}")

			if invalidMDTitels:
				titel = extractHeaderValues(content, 'title')
				logging.warning(f"Titel '{invalidMDTitels}' is/zijn verkeerd opgemaakt in bestand: '{filePath}'")
				errors.append(ERROR_INVALID_MD_TITELS)
				errors.extend([f"- {error.replace('**', '\\*\\*')}" for error in invalidMDTitels])

			if invalidMDText:
				logging.warning(f"Tekst is verkeerd opgemaakt in bestand: '{filePath}'")
				errors.append(ERROR_INVALID_MD_BOLD_TEXT)
				errors.extend([f"- {error.replace('**', '\\*\\*')}" for error in invalidMDText])

		# Combine all errors
		errors = mediaErrors + tagErrors + errors

        # If there are any errors, the file is considered a draft unless the ignore tag is used
		if errors and not isIgnore:
			isDraft = True

		appendFileToSpecificList(errors, todoItems, filePath, taxonomie, newTags)
		saveParsedFile(filePath, taxonomie, newTags, difficulty, isDraft, isIgnore, content, destFilePath)

# Fill the different lists used for the report
def appendFileToSpecificList(errors, todoItems, filePath, taxonomie, tags):
	if errors:
		if todoItems:
			icon = TODO_ITEMS_ICON
			targetList = WIPFiles   
		elif ERROR_IGNORE_TAG_USED in errors:
			icon = WARNING_ICON
			targetList = ignoredFiles
		elif ERROR_NO_TAXCO_FOUND in errors or ERROR_TAXCO_NOT_NEEDED in errors:
			icon = FAIL_CROSS_ICON
			targetList = failedFiles
		else:
			icon = WARNING_ICON
			targetList = failedFiles
	else:
		icon = SUCCESS_ICON
		targetList = parsedFiles

	targetList.append(createFileReportRow(icon, filePath, taxonomie, tags, errors))

# Combines everything into a new md file
def saveParsedFile(filePath, taxonomie, tags, difficulty, isDraft, isIgnore, content, destFilePath):
    newContent = (
        f"---\ntitle: {filePath.stem}\ntaxonomie: {taxonomie}\ntags:\n" +
        '\n'.join([f"- {tag}" for tag in tags]) +
        "\n"
    )

    if difficulty:
        newContent += "difficulty: " + ''.join([f"{level}" for level in difficulty]) + "\n"
        
    if isDraft:
        newContent += "draft: true \n"
        
    if isIgnore:
        newContent += "ignore: true \n"

    newContent += "---" + content.split('---', 2)[-1]

    destFilePath.parent.mkdir(parents=True, exist_ok=True)

    with open(destFilePath, 'w', encoding='utf-8') as f:
        f.write(newContent)
