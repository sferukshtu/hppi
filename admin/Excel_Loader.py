import datetime, xlrd, re
from pymongo import MongoClient
""" For staff collection email should be a unique index! """
""" This should be done before collection population: """
""" db.staff.createIndex( { email: 1 }, { unique: true } )  """


def main():
    excel = raw_input("Enter excel file to load: ")
    collection = raw_input("Enter collection name: ")
    client = MongoClient("localhost", 27017)['hppi'][collection]
    rd = xlrd.open_workbook(excel)
    sheet = rd.sheet_by_index(0)
    header = sheet.row_values(0)  # column headers

    client.drop()
    for rownum in range(1, sheet.nrows):
        row = sheet.row_values(rownum)  # row values
        data = {}
        for el in range(len(header)):
            if sheet.cell(rownum, el).ctype == 3:  # i.e. datetype
                dt = datetime.datetime(*xlrd.xldate_as_tuple(row[el], rd.datemode))  # convert date from excel
            else:
                dt = row[el]
            data[header[el]] = dt  # pack data in a dictionary data[name] = value
        client.insert_one(data)  # filling mongodb's collection named "staff" with data

if __name__ == '__main__':
    main()
