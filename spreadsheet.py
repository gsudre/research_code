''' Script to return a dictionary subjs with the string name and subject status
    from the Excel spreadsheet that Bethany keeps.
'''
# Gustavo Sudre, 01/2013


def get_subjects_from_excel():
    fname = r'/Users/sudregp/Documents/Bethany_MEGRest_Analysis_Notes_Sept11.xlsx'

    from openpyxl.reader.excel import load_workbook
    wb = load_workbook(filename=fname)
    ws = wb.worksheets[0]

    subjs = {}
    cnt = 1

    # while we still have something written in the first collumn
    while ws.cell('A' + str(cnt)).value is not None:
        # check if we should use the data or not
        if ws.cell('F' + str(cnt)).value == 'Y':
            subjs[str(ws.cell('D' + str(cnt)).value)] = str(ws.cell('L' + str(cnt)).value)
        cnt = cnt + 1

    return subjs


def get_all_subjects():
    fname = r'/Users/sudregp/Documents/Bethany_MEGRest_Analysis_Notes_Sept11.xlsx'

    from openpyxl.reader.excel import load_workbook
    wb = load_workbook(filename=fname)
    ws = wb.worksheets[0]

    subjs = {}

    # start from the second row down
    cnt = 2

    # while we still have something written in the first collumn
    while ws.cell('A' + str(cnt)).value is not None:
        # if there is something in the ID column
        if isinstance(ws.cell('D' + str(cnt)).value, unicode):
            subjs[str(ws.cell('D' + str(cnt)).value)] = str(ws.cell('L' + str(cnt)).value)

        cnt = cnt + 1

    return subjs
