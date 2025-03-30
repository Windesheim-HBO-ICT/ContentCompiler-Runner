import re, logging
from compiler.config import (
    dataset, contentReport, PROCES_COL, PROCESSTAP_COL, TC1_COL, TC2_COL, TC3_COL, 
    ERROR_INVALID_TAXCO, ERROR_NO_TAXCO_FOUND, ERROR_DOUBLE_PAGE_FRONTMATTER,
    ERROR_TAXCO_NOT_FOUND, ERROR_TAXCO_NOT_NEEDED, FILE_HAS_IGNORE_TAG,
    DOUBLE_BOLD_IN_TEXT_REGEX, TAXONOMIE_REGEX, TODO_REGEX, TITLE_REGEX, FRONTMATTER_REGEX, FRONTMATTER_KEY_REGEX
)
from compiler.report.generateTaxcoReport import updateProcessReportData, updateSubjectReportData


"""
Generate tags based on the taxonomie values
Args:
    taxonomies (list): List of taxonomie values.
    existingTags (list): List of existing tags.
    filePath (str): Path to the markdown file being processed.
"""
def generateTags(taxonomies, existingTags, filePath):
    tags = []
    errors = []
    combinedTags = []
    taxonomieTags = []

    if taxonomies is not None and taxonomies != ['None'] and taxonomies != [''] and taxonomies != []:
        for taxonomie in taxonomies:
            # Check if the taxonomie is in the correct format
            if not re.match(TAXONOMIE_REGEX, taxonomie):
                errors.append(f"{ERROR_INVALID_TAXCO} `{taxonomie}`")
                logging.warning(f"{ERROR_INVALID_TAXCO} `{taxonomie}` in bestand: {filePath}")
                continue

            # Split the taxonomie in it's different parts
            extractedTC1, extractedTC2, extractedTC3, extractedTC4 = splitTaxonomie(taxonomie)
            
            # If the parts are all valid
            if extractedTC1 and extractedTC2 and extractedTC3 and extractedTC4:
                # Loop trough every row in the dataset
                for row in dataset:
                    # Check if the first part of the taxonomie is equal to the TC1 column
                    if row[TC1_COL] == extractedTC1:                        
                        # Check if the second part of the taxonomie is equal to the TC2 column
                        if row[TC3_COL] in contentReport and row[TC3_COL] == extractedTC3:
                            # Adds the HBO-i/niveau tag
                            newTag = "HBO-i/niveau-" + extractedTC2
                            if newTag not in tags:
                                tags.append(newTag)
    
                            # Adds the proces
                            if row[PROCES_COL] not in tags:
                                tags.append(row[PROCES_COL])

                            # Adds the processtap
                            if row[PROCESSTAP_COL] not in tags:
                                tags.append(row[PROCESSTAP_COL])

                            # Check if the third part of the taxonomie is in the tags table
                            if row[TC3_COL] not in tags:
                                tags.append(row[TC3_COL])
                                
                            # Check if the full taxonomie is already in the taxonomie tags
                            if taxonomie not in taxonomieTags:
                                taxonomieTags.append(taxonomie)

                            # Check if the taxonomie is not needed
                            splittedRow =  row[TC2_COL].split(',')
                            if splittedRow[int(extractedTC2)-1] == "X": 
                                errors.append(f"{ERROR_TAXCO_NOT_NEEDED} `{taxonomie}`")
                                logging.warning(f"{ERROR_TAXCO_NOT_NEEDED} `{taxonomie}` in bestand: {filePath}")

                            # Update the process report data with the new values
                            # This is needed so the report has the correct data
                            # Before the script runs it pre-fills the report with all the taxonomies
                            # This is done so the report has all the taxonomies even if they are not used
                            # After this the report is updated with the correct data
                            updateProcessReportData(extractedTC1, extractedTC2)
                            updateSubjectReportData(extractedTC1, extractedTC2, extractedTC3, extractedTC4)

            # If no tags were found, add an error
            if tags == [] and not errors:
                errors.append(f"{ERROR_TAXCO_NOT_FOUND} `{taxonomie}`")   
                logging.warning(f"{ERROR_TAXCO_NOT_FOUND} `{taxonomie}` in bestand: {filePath}")
    else:
        errors.append(f"{ERROR_NO_TAXCO_FOUND}")
        logging.warning(f"{ERROR_NO_TAXCO_FOUND} in bestand: {filePath}")

    # Combine the existing tags with the new tags
    combinedTags.extend(existingTags or [])
    combinedTags.extend(tags or [])
    combinedTags.extend(taxonomieTags or [])
    
    # Sort combined_tags so that "HBO-i/niveau-" tags are moved to the start
    combinedTags = sorted(combinedTags, key=lambda tag: (not tag.startswith("HBO-i/niveau-"), tag))

    return list(dict.fromkeys(combinedTags)), errors

def splitTaxonomie(taxonomie):
    return taxonomie.split('.')

def extractHeaderValues(content: str, fieldName: str):
    """
    Extracts values associated with a specific field name in the header of a markdown file.
    """
    lines = content.splitlines()
    values = []
    field_prefix = f'{fieldName}:'

    for i, line in enumerate(lines):
        if line.startswith(field_prefix):
            # Extract single value if present on the same line
            value = line[len(field_prefix):].strip()
            if value:
                values.append(value)
            else:
                # Extract list values if present in subsequent lines
                for subLine in lines[i + 1:]:
                    subLine = subLine.strip()
                    if subLine.startswith('- '):
                        values.append(subLine[2:].strip())
                    else:
                        break
            break

    return values or None

# Helper function to find all the To-Do items in the content of a markdown file.	
def findWIPItems(content):
    return re.findall(TODO_REGEX, content)

# Helper function to check if a file has an ignore tag.
def checkForIgnoreTag(filePath, content):
    ignoreTAG = extractHeaderValues(content, 'ignore')

    if ignoreTAG and "true" in ignoreTAG:
        logging.info(f"{FILE_HAS_IGNORE_TAG} `{filePath}`")
        return True

    return False

# Helper function to check if the filename matches the title tag in the markdown file.
def isFileNameAndTitelEqual(filePath, content) -> bool:
    titel = extractHeaderValues(content, 'title')
    fileName = filePath.stem
    
    return titel == [fileName]

# Helper function to check for bold in markdown titel
def checkForBoldInTitel(content):
    invalidTitels = []
    
    title_regex = re.compile(TITLE_REGEX, re.MULTILINE)
    mdContentTitels = re.findall(title_regex, content)
    for level, mdContentTitel in mdContentTitels:
        if '**' in mdContentTitel:
            invalidTitels.append(mdContentTitel)

    return invalidTitels

# Helper function to check for double bold text in markdown
def checkForDoubleBoldInText(content):
    invalidTexts = []
    
    mdContentTexts = re.findall(DOUBLE_BOLD_IN_TEXT_REGEX, content)
    for mdContentText in mdContentTexts:
        invalidTexts.append(mdContentText)

    return invalidTexts

# Helper function to check for double page frontmatter
def checkForDoublePageFrontmatter(filePath, content):
    frontmatter_match = re.search(FRONTMATTER_REGEX, content, re.DOTALL | re.MULTILINE)
    if not frontmatter_match:
        return []
    
    frontmatter = frontmatter_match.group(1)
    keys = re.findall(FRONTMATTER_KEY_REGEX, frontmatter, re.MULTILINE)
    duplicate_keys = {key for key in keys if keys.count(key) > 1}
    
    errors = []
    if duplicate_keys:
        error_msg = f"{ERROR_DOUBLE_PAGE_FRONTMATTER}: '{', '.join(duplicate_keys)}'"
        if filePath:
            logging.warning(error_msg)
        errors.append(error_msg)
    return errors