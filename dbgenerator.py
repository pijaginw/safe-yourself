from sqlite3 import *

db = connect('dbase.db')
cur = db.cursor()


db.execute('CREATE TABLE dbase (login TEXT, password TEXT)')

db.execute("ALTER TABLE dbase ADD COLUMN '{cn}' INT DEFAULT 0".format(cn='counter'))

db.execute('CREATE TABLE tokens (token TEXT, isBeingUsed INT DEFAULT 0, used INT DEFAULT 0)')

db.commit()
db.close()