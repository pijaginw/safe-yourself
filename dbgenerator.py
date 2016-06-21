from sqlite3 import *

db = connect('dbase.db')
cur = db.cursor()


db.execute('CREATE TABLE dbase (login TEXT, password TEXT)')

db.execute("ALTER TABLE dbase ADD COLUMN '{cn}' INT DEFAULT 0".format(cn='counter'))

db.commit()
db.close()