from compiler.report.table import generateMarkdownTable
from compiler.config import taxcoReport, contentReport
from compiler.config import LT, DT, OI, PI, FAIL_CIRCLE_ICON, SUCCESS_ICON, NOT_NECESSARY_ICON, TAXCO_REPORT_PATH


# Update the taxco list with the new values
def updateProcessReportData(tc1, tc2):
    # Helper function to update the TC2 status for a given index
    def updateProcessReportRow(tc1, tc2, index):
        # Check if the tc2 matches the index and the current status is not NOT_NECESSARY_ICON
        if tc2 == str(index + 1) and taxcoReport[tc1]['TC2'][index] != NOT_NECESSARY_ICON:
            # Update the status to 'v' (success)
            taxcoReport[tc1]['TC2'][index] = 'v'

    # Loop through the three levels and update the process report row
    for i in range(3):
        updateProcessReportRow(tc1, tc2, i)

# Update the content list data with the new values.
def updateSubjectReportData(tc1, tc2, tc3, fileType):
    # Helper function to update the record with the new values
    def updateSubjectReportRow(tc1, tc2, tc3, fileType, searchType):
        fileTypeMapping = {
            "LT": "Leertaken",
            "OI": "Ondersteunende-informatie",  
            "PI": "Procedurele-informatie",     
            "DT": "Deeltaken"                   
        }

        # Convert fileType if it exists in the mapping
        fileTypeFull = fileTypeMapping.get(fileType, fileType)
        contentReport[tc3][tc1][searchType] = [
            'v' if fileTypeFull == searchType and tc2 == '1' and contentReport[tc3][tc1][searchType][0] != NOT_NECESSARY_ICON else contentReport[tc3][tc1][searchType][0], 
            'v' if fileTypeFull == searchType and tc2 == '2' and contentReport[tc3][tc1][searchType][1] != NOT_NECESSARY_ICON else contentReport[tc3][tc1][searchType][1], 
            'v' if fileTypeFull == searchType and tc2 == '3' and contentReport[tc3][tc1][searchType][2] != NOT_NECESSARY_ICON else contentReport[tc3][tc1][searchType][2]
        ]

    contentReport[tc3][tc1]['TC2'] = ['v' if tc2 == '1' and contentReport[tc3][tc1]['TC2'][0] != NOT_NECESSARY_ICON else contentReport[tc3][tc1]['TC2'][0], 'v' if tc2 == '2' and contentReport[tc3][tc1]['TC2'][1] != NOT_NECESSARY_ICON else contentReport[tc3][tc1]['TC2'][1], 'v' if tc2 == '3' and contentReport[tc3][tc1]['TC2'][2] != NOT_NECESSARY_ICON else contentReport[tc3][tc1]['TC2'][2]]
    updateSubjectReportRow(tc1, tc2, tc3, fileType, LT)
    updateSubjectReportRow(tc1, tc2, tc3, fileType, OI)
    updateSubjectReportRow(tc1, tc2, tc3, fileType, PI)
    updateSubjectReportRow(tc1, tc2, tc3, fileType, DT)

# Generate the report based on the taxonomie report, success, and failed reports.
def generateTaxcoReport():
    with open(TAXCO_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write('---\ndraft: true\n---\n')
        
        f.write('## Rapport 1 - Processtappen\n')
        f.write('*Doel: achterhalen welke processtappen nog helemaal niet zijn geïmplementeerd*\n\n')
        f.write('- ✅ Er bestaat een bestand met deze taxonomiecode op dit niveau \n')
        f.write('- ⛔️ Er is geen enkel bestand met deze taxonomiecode op dit niveau \n')
        f.write('- 🏳️ De taxonomiecode wordt niet aangeboden op dit niveau (X in de Dataset) \n')
        f.write('\n')
        f.write(generateProcessTable())

        f.write('\n\n')

        f.write('## Rapport 2 - Onderwerpen Catalogus\n')
        f.write('*Doel: Lijst met onderwerpen + gekoppelde taxonomie code voor inzicht in aangeboden onderwerpen.*\n')
        f.write('Bij kolom *TC2*, *Leertaken*, *Ondersteunende informatie*, *Procedurele informatie* en *Deeltaken* zijn drie tekens aanwezig om de drie HBO-i niveaus weer te geven\n\n')
        f.write('- ✅ Het onderwerp met taxonomie code wordt aangeboden op het aangegeven niveau \n')
        f.write('- ⛔️ Het onderwerp met taxonomie code wordt **niet** aangeboden op het aangegeven niveau \n')
        f.write('- 🏳️ Het onderwerp hoeft met deze taxonomie code niet aangeboden te worden op het aangegeven niveau \n')
        f.write('\n')
        f.write(generateSubjectTable())

# Format the report table for the process table
def generateProcessTable():
    # Define the headers for the process table
    headers = ["TC1", "Proces", "Processtap", "Niveau 1", "Niveau 2", "Niveau 3"]
    rows = []

    # Helper function to get the status icon for a given level
    def getStatus(level):
        if level == 'v' or level == 'g':
            return SUCCESS_ICON
        elif level == 'x':
            return FAIL_CIRCLE_ICON
        else:
            return NOT_NECESSARY_ICON

    # Loop through the taxco report and generate the table rows
    for tc, details in taxcoReport.items():
        proces = details.get('Proces', '')
        processtap = details.get('Processtap', '')
        tc2_levels = details.get('TC2', {})
        niveau_1 = getStatus(tc2_levels[0])
        niveau_2 = getStatus(tc2_levels[1])
        niveau_3 = getStatus(tc2_levels[2])

        # Append the row to the list of rows
        rows.append([tc, proces, processtap, niveau_1, niveau_2, niveau_3])

    # Generate the markdown table using the headers and rows
    return generateMarkdownTable(headers, rows)

# Format the report for the subject table
def generateSubjectTable():
    headers = ["TC3", "TC1", "TC2", LT, OI, PI, DT]
    rows = []

    # Helper function to get the status of the value
    def getStatus(value):
        if value == 'v' or value == 'g':
            return SUCCESS_ICON
        elif value != NOT_NECESSARY_ICON:
            return FAIL_CIRCLE_ICON
        else:
            return NOT_NECESSARY_ICON

    # Helper function to get the status for each level
    def getStatusForLevels(levels):
        return ' '.join([getStatus(level) for level in levels])

    # Loop through the content report and generate the table
    for tc3, row in contentReport.items():
        for tc1, other in row.items():
            tc2 = getStatusForLevels(other.get('TC2', [''] * 3))
            leertaak = getStatusForLevels(other.get(LT, [''] * 3))
            ondersteunende_informatie = getStatusForLevels(other.get(OI, [''] * 3))
            procedurele_informatie = getStatusForLevels(other.get(PI, [''] * 3))
            deeltaak = getStatusForLevels(other.get(DT, [''] * 3))

            rows.append([tc3, tc1, tc2, leertaak, ondersteunende_informatie, procedurele_informatie, deeltaak])

    return generateMarkdownTable(headers, rows)
