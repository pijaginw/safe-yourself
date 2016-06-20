from sqlite3 import *

db = connect('dbase.db')
cur = db.cursor()


db.execute('CREATE TABLE dbase (login TEXT, password TEXT)')

db.execute("INSERT INTO dbase (login, password) VALUES ('nanan1', 'pass')")
db.execute("INSERT INTO dbase (login, password) VALUES ('120056', 'top secret')")

db.execute("ALTER TABLE dbase ADD COLUMN '{cn}' INT DEFAULT 0".format(cn='counter'))

db.commit()

cur.execute('SELECT * FROM dbase')
print cur.fetchall()

db.close()