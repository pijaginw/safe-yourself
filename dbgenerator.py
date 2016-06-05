from sqlite3 import *

db = connect('dbase.db')
cur = db.cursor()


db.execute('CREATE TABLE dbase (login TEXT, password TEXT)')

db.execute("INSERT INTO dbase (login, password) VALUES ('aa153454', 'test')")
db.execute("INSERT INTO dbase (login, password) VALUES ('120056', 'top secret')")

db.commit()
db.close()