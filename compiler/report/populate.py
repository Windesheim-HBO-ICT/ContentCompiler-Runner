from compiler.config import dataset, taxcoReport, contentReport
from compiler.config import TC1_COL, TC2_COL, TC3_COL, PROCES_COL, PROCESSTAP_COL, NOT_NECESSARY_ICON, LT_COL, DT_COL, OI_COL, PI_COL, LT, DT, OI, PI

"""
Fills the taxco report with the data from the dataset.
Every TC1 code is the unique identifier.
"""
def populateTaxcoReport():
    global taxcoReport

    for row in dataset:
        tc1 = row[TC1_COL]
        tc2 = row[TC2_COL]
        proces = row[PROCES_COL]
        processtap = row[PROCESSTAP_COL]

        if tc1 in taxcoReport:
            updateTaxcoReport(tc1, tc2)
        else:
            addNewTaxcoReportEntry(tc1, tc2, proces, processtap)

"""
Updates an existing entry in the taxco report.
"""
def updateTaxcoReport(tc1, tc2):
    splittedTc2 = tc2.split(',')
    for index in range(1, 3):
        if taxcoReport[tc1]['TC2'][index] == '🏳️' and splittedTc2[index] != '🏳️':
            taxcoReport[tc1]['TC2'][index] = splittedTc2[index]

def addNewTaxcoReportEntry(tc1, tc2, proces, processtap):
    splittedTc2 = tc2.split(',')
    taxcoReport[tc1] = {
        "Proces": proces,
        "Processtap": processtap,
        'TC2': [NOT_NECESSARY_ICON if splittedTc2[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedTc2[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedTc2[2] == 'X' else 'x']
    }

"""
Fills the Report 2 data with the data from the dataset.
Every unique TC3 and TC1 combination will be added to the Report 2 data.
"""
def populateContentReport():
    global contentReport

    for row in dataset:
        # Extract relevant columns from the dataset row
        tc1 = row[TC1_COL]
        tc2 = row[TC2_COL]
        tc3 = row[TC3_COL]
        lt = row[LT_COL]
        oi = row[OI_COL]
        pi = row[PI_COL]
        dt = row[DT_COL]

        # Initialize a new entry for TC3 if it doesn't exist
        if tc3 not in contentReport:
            contentReport[tc3] = {}

        # Add a new entry for TC1 under the current TC3 if it doesn't exist
        if tc1 not in contentReport[tc3]:
            contentReport[tc3][tc1] = {
                'TC2': processColumn(tc2),
                LT: processColumn(lt),
                OI: processColumn(oi),
                PI: processColumn(pi),
                DT: processColumn(dt),
            }

"""
Processes a column of data, splitting it by commas and replacing 'X' with NOT_NECESSARY_ICON.
"""
def processColumn(columnData):
    return [NOT_NECESSARY_ICON if val == 'X' else 'x' for val in columnData.split(',')]