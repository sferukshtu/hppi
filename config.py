from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'devil in the sky'
DB_NAME = 'hppi'

DATABASE = MongoClient()[DB_NAME]
STAFF = DATABASE.staff
SETTINGS = DATABASE.settings

DEBUG = True
