from config import SRC_DIR

# Generate a markdown table string from a list of rows and headers.
def generateMarkdownTable(headers, rows):
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in rows:
        table += "| " + " | ".join(row) + " |\n"
    return table

# Create a new row in the file report based on the status, file path, taxonomie, and tags.
def createFileReportRow(status, filePath, taxonomie, tags, errors):
    return {
        "status": status,
        "file": filePath.stem,
        "path": str(filePath.relative_to(SRC_DIR)),
        "taxonomie": '<br>'.join(taxonomie) if taxonomie else "N/A",
        "tags": '<br>'.join(tags) if tags else "N/A",
        "errors": '<br>'.join(errors) if errors else "N/A"
    }

# Format the success or failed report table based on a list.
def formatFileReportTable(fileReport):
    headers = ["Status", "File", "Path", "Taxonomie", "Tags", "Errors"]
    rows = [[
        file['status'], 
        file['file'], 
        file['path'], 
        file['taxonomie'], 
        file['tags'],
        file['errors']
     ] for file in fileReport]

    return generateMarkdownTable(headers, rows)

# Create a row for the image report table
def createMediaTableRow(statusIcon, fileName, filePath, error):
    return {
        "status" : statusIcon,
        "file": fileName,
        "path": str(filePath.relative_to(SRC_DIR)),
        "error": error,
    }

# Format the image report table with specific headers and rows
def formatMediaReportTable(mediaReport):
    headers = ["Status", "Image", "Path", "Error"]
    rows = [[
        file['status'], 
        file['file'], 
        file['path'],
        file['error']
    ] for file in mediaReport]

    return generateMarkdownTable(headers, rows)
