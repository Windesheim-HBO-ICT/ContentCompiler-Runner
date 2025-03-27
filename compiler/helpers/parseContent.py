import logging
from pathlib import Path
from compiler.config import (
	SRC_DIR, DEST_DIR,
    failedFiles, ignoredFiles, parsedFiles, WIPFiles,
	SUCCESS_ICON, TODO_ITEMS_ICON, WARNING_ICON,
    FILE_HAS_IGNORE_TAG, ERROR_INVALID_MD_BOLD_TEXT,
    ERROR_INVALID_MD_TITELS, ERROR_NO_TAXCO_FOUND, ERROR_TAXCO_NOT_NEEDED,
    ERROR_TITEL_NOT_EQUAL_TO_FILENAME, ERROR_WIP_FOUND, FAIL_CROSS_ICON, IGNORE_FOLDERS,
)
from compiler.helpers.media import processMediaLinks
from compiler.report.table import createFileReportRow
from compiler.helpers.markdownUtils import (
    checkForBoldInTitel, checkForDoubleBoldInText, checkForDoublePageFrontmatter,
    isFileNameAndTitelEqual, extractHeaderValues, findWIPItems, generateTags, checkForIgnoreTag
)


# Update markdown files in the source directory
def parseMarkdownFiles(skipValidateDynamicLinks):
	# Loop through all markdown files in the source directory
	for filePath in Path(SRC_DIR).rglob('*.md'):
		# Skip certain folders
		if shouldSkipFile(filePath):
			logging.info(f"Skipping folder: {filePath}")
			continue
    
		destFilePath = computeDestFilePath(filePath)
  
		# Start reading the content of the file
		content = readFileContent(filePath)
		existingTags = extractHeaderValues(content, 'tags')
		difficulty = extractHeaderValues(content, 'difficulty')
  
		# Check for double page frontmatter
		errors = checkForDoublePageFrontmatter(filePath, content)
  
		# Process media links
		updatedContent, mediaErrors = processMediaLinks(filePath, content, skipValidateDynamicLinks)
		errors.extend(mediaErrors)
  
		# Check if file has an ignore tag; if so, mark and skip further validations.
		hasIgnoreTag = checkForIgnoreTag(filePath, updatedContent)
  
		# If the file has an ignore tag, skip the taxonomie and tag generation
		if not hasIgnoreTag:
			# Process taxonomie and generate tags
			taxonomie, newTags, tagErrors = processTags(filePath, content, existingTags)
			errors.extend(tagErrors)

			# Validate content (WIP items, title matching, markdown formatting)
			validationErrors, todoItems = validateContent(filePath, content)
			errors.extend(validationErrors)
		else:
			taxonomie, newTags, todoItems = [], [], []
			errors.append(FILE_HAS_IGNORE_TAG)

		# If there are any errors, the file is considered a draft unless the ignore tag is used
		isDraft = True if errors and not hasIgnoreTag else False

		appendFileToSpecificList(errors, todoItems, filePath, taxonomie, newTags)
		saveParsedFile(filePath, taxonomie, newTags, difficulty, isDraft, hasIgnoreTag, content, destFilePath)

# Helper function to determine if a file should be skipped
def shouldSkipFile(filePath):
    return any(folder in str(filePath) for folder in IGNORE_FOLDERS)

# Helper function to compute the destination file path
def computeDestFilePath(filePath):
    relativePath = filePath.relative_to(SRC_DIR)
    return DEST_DIR / relativePath

# Helper function to read the content of a file
def readFileContent(filePath):
    with open(filePath, 'r', encoding='utf-8') as f:
        return f.read()

# Helper function to process the tags of a markdown file
def processTags(filePath, content, existingTags):
    taxonomie = extractHeaderValues(content, 'taxonomie')
    newTags, tagErrors = generateTags(taxonomie, existingTags, filePath)
    return taxonomie, newTags, tagErrors

# Helper function to validate the content of a markdown file
def validateContent(filePath, content):
	errors = []
	todoItems = findWIPItems(content)
	fileNameAndTitelEqual = isFileNameAndTitelEqual(filePath, content)
	invalidMDTitels = checkForBoldInTitel(content)
	invalidMDText = checkForDoubleBoldInText(content)

	if todoItems:
		errors.append(f"{ERROR_WIP_FOUND}<br>{'<br>'.join(todoItems)}")

	if not fileNameAndTitelEqual:
		titel = extractHeaderValues(content, 'title')
		if isinstance(titel, list):
			titel = titel[0] if titel else ""
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

	return errors, todoItems

# Fill the different lists used for the report
def appendFileToSpecificList(errors, todoItems, filePath, taxonomie, tags):
	if errors:
		if FILE_HAS_IGNORE_TAG in errors:
			icon = WARNING_ICON
			targetList = ignoredFiles
		elif ERROR_NO_TAXCO_FOUND in errors or ERROR_TAXCO_NOT_NEEDED in errors:
			icon = FAIL_CROSS_ICON
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

# Combines everything into a new md file
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
