# -*- coding: UTF-8 -*-
import datetime, xlrd, re
from pymongo import MongoClient
""" For staff collection email should be a unique index! """
""" This should be done before the very first collection population: """
""" db.staff.createIndex( { email: 1 }, { unique: true } )  """
""" db.settings.insert({set_id:"prnd","prnd":""}) """


def fields(titles, collection):
    """ Column names must be named only as below"""
    if (collection == 'staff'):
        names = ["surname", "first_name", "middle_name", "date_of_birth", "graduated",
                            "graduated_year", "degree", "email", "position", "lab"]
    else:
        return 0
    is_identical = titles.union(set(names)) - titles.intersection(set(names))
    return len(is_identical)


def main():
    excel = raw_input("Enter excel file to load: ")
    collection = raw_input("Enter collection (if empty staff collection will be populated): ")
    # collection = ['staff', collection][collection == collection]
    collection = collection if collection else 'staff'
    client = MongoClient("localhost", 27017)['hppi'][collection]
    rd = xlrd.open_workbook(excel)
    sheet = rd.sheet_by_index(0)
    header = sheet.row_values(0)  # column headers
    if fields(set(header), collection) == 0:
        # client.drop()
        for rownum in range(1, sheet.nrows):
            row = sheet.row_values(rownum)  # row values
            data = {}
            for el in range(len(header)):
                if sheet.cell(rownum, el).ctype == 3:  # i.e. datetype
                    dt = datetime.datetime(*xlrd.xldate_as_tuple(row[el], rd.datemode))  # convert date from excel
                else:
                    dt = row[el]
                data[header[el]] = dt  # pack data in a dictionary data[name] = value
            if collection == 'staff':
                data["access"] = 1  # data access right by default (can edit only themselves)
                data["pubs"] = 0  # num of pubs
                data["prnd"] = 0  # for prnd
                data["prnd_data"] = {}
                data["publist"] = {}
                data["graduated_year"] = int(data["graduated_year"])
                if not re.match(r"^\S+@\S+\.\S+$", data["email"]):
                    print "No correct email for someone with the surname", data["surname"], "skipping"
                else:
                    user = client.find_one({"email": data["email"]})
                    if not user:
                        client.insert_one(data)  # filling mongodb's collection named "staff" with data
                    else:
                        print "Staff member", data["surname"], "with email", data["email"], "already present in DB, entry is updated"
                        client.update_one({'email': data["email"]}, {'$set': data})
            else:
                client.drop()
                client.insert_one(data)
    else:
        print "Column names do not correspond to the specification!"


if __name__ == '__main__':
    main()
