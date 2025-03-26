from report.table import formatFileReportTable, formatMediaReportTable
from config import WIPFiles, failedFiles, failedMediaFiles, parsedFiles, ignoredFiles, CONTENT_REPORT_PATH
from config import WARNING_ICON, FAIL_CROSS_ICON


# Generate the report based on the taxonomie report, success, and failed reports.
def generateContentReport():
    with open(CONTENT_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write('---\ndraft: true\n---\n')
        
        f.write("## Work-in-progress bestanden\n")
        f.write('*Doel: De onderstaande bestanden hebben nog todo items in de markdown staan.*\n')
        f.write('Deze todo items moeten nog worden afgehandeld.\n')
        f.write('\n')
        f.write(formatFileReportTable(sorted(WIPFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Gefaalde bestanden\n")
        f.write("*Doel: De onderstaande bestanden zijn niet succesvol verwerkt.*\n\n")
        f.write(FAIL_CROSS_ICON + ' Dit bestand bevat nog geen taxonomie codes.\n')
        f.write(WARNING_ICON + ' Dit bestand bevat fouten. Zie de *Errors* kolom.\n')
        f.write('\n')
        f.write(formatFileReportTable(sorted(failedFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Gefaalde media bestanden\n")
        f.write("*Doel: De onderstaande media bestanden worden niet gebruikt in een bestand.*\n\n")
        f.write(formatMediaReportTable(sorted(failedMediaFiles, key=lambda x: x['file'])))
        
        f.write('\n\n')
        
        f.write("## Genegeerde bestanden\n")
        f.write("*Doel: De onderstaande bestanden worden genegeerd.*\n\n")
        f.write(formatFileReportTable(sorted(ignoredFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Geslaagde bestanden\n")
        f.write("*Doel: De onderstaande bestanden zijn succesvol verwerkt.*\n")
        f.write('\n')
        f.write(formatFileReportTable(sorted(parsedFiles, key=lambda x: x['file'])))
