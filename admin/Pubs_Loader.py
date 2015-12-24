import datetime, xlrd
from pymongo import MongoClient
# import re


def fields(titles):
    """ Column names must be named only as below"""
    names = ["title", "authors", "abstract", "url", "date", "journal", "pubinfo"]
    is_identical = titles.union(set(names)) - titles.intersection(set(names))
    return len(is_identical)


def main():
    client = MongoClient('localhost', 27017)
    db = client.hppi
    excel = raw_input("Enter excel file of publications to load: ")
    email = raw_input("Enter author's email: ")
    rd = xlrd.open_workbook(excel)
    sheet = rd.sheet_by_index(0)

    header = sheet.row_values(0)  # column headers
    if fields(set(header)) == 0:
        for rownum in range(1, sheet.nrows):
            row = sheet.row_values(rownum)  # row values
            # print row
            data = {}

            for el in range(len(header)):
                if header[el] == "date":
                    dt = datetime.datetime(*xlrd.xldate_as_tuple(row[el], rd.datemode))  # convert date from excel
                else:
                    dt = row[el]
                data[header[el]] = dt  # pack data in a dictionary data[name] = value
            data["art_id"] = rownum
            db.staff.update_one({'email': email}, {'$push': {'publist': data}})
    else:
        print "Column names do not correspond to the specification!"


if __name__ == '__main__':
    main()
