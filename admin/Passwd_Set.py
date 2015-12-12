from werkzeug.security import generate_password_hash
import datetime
from pymongo import MongoClient
# from pymongo.errors import DuplicateKeyError


def main():
    # Connect to the DB
    collection = MongoClient()["hppi"]["staff"]
    # Data fields to create unless user exists
    data = {"surname": "", "first_name": "", "middle_name": "", "lab": "", "position": "",
            "date_of_birth": datetime.datetime(1900, 01, 01), "graduated": "", "graduated_year": "", "degree": ""}
    # Ask for data to store
    email = raw_input("Enter email of the user: ")
    password = raw_input("Enter password for the user: ")
    pass_hash = generate_password_hash(password, method='pbkdf2:sha256')
    access = raw_input("Enter access rights for the user, 0 for reading, 1 for editing own entry, 2 for full access: ")
    # Insert the user in the DB
    user = collection.find_one({"email": email})
    if not user:
        collection.insert({"email": email, "password": pass_hash, "access": access})
        collection.update_one({'email': email}, {'$set': data})
        print "User created."
    else:
        print "User already present in DB. Password is updated"
        collection.update_one({'email': email}, {'$set': {'password': pass_hash, "access": access}})

if __name__ == '__main__':
    main()
