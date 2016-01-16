from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'devil in the sky'
DB_NAME = 'hppi'

DATABASE = MongoClient()[DB_NAME]
STAFF = DATABASE.staff
RATING = DATABASE.rating
SETTINGS = DATABASE.settings
FILE_EXTENSIONS = set(['xls', 'xlsx'])
DEBUG = True
