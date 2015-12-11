import datetime, xlrd
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.hppi
rd = xlrd.open_workbook("excel/Staff.xlsx")
sheet = rd.sheet_by_index(0)

header = sheet.row_values(0)  # column headers

db.staff.drop()
for rownum in range(1, sheet.nrows):
    row = sheet.row_values(rownum)  # row values
    # print row
    data = {}
    for el in range(len(header)):
        if header[el] == "date_of_birth":
            dt = datetime.datetime(*xlrd.xldate_as_tuple(row[el], rd.datemode))  # convert date formatting from excel
        else:
            dt = row[el]
        data[header[el]] = dt  # pack data in a dictionary data[name] = value
    data["position"] = ""
    data["lab"] = ""
    result = db.staff.insert_one(data)  # filling mongodb's collection named "staff" with data
