import sqlite3
from passlib.hash import pbkdf2_sha256

def addToDatabase(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('INSERT INTO dbase (login, password) VALUES (?, ?)', (login, hashPassword(password)))
  conn.commit()
  conn.close()

def isUserInDatabase(login, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('SELECT * FROM dbase WHERE login=?', (login, ))
  conn.commit()
  result = c.fetchall()
  conn.close()

  if len(result) == 0:
    return False
  return True

def isPasswordCorrect(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('SELECT password FROM dbase WHERE login=?', (login, ))
  conn.commit()
  result = c.fetchall()
  conn.close()
  return pbkdf2_sha256.verify(password, str(result[0][0]))

def changePassword(login, newpass, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('UPDATE dbase SET password=? WHERE login=?', (hashPassword(newpass), login))
  conn.commit()
  conn.close()

def addNoteToDatabase(note, login, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  # c.execute('SELECT * FROM dbase')
  # print c.fetchall()
  c.execute('SELECT counter FROM dbase WHERE login=?', (str(login), ))
  conn.commit()
  res = c.fetchall()

  if len(res) == 1:
    res = res[0][0]

  new_column = 'note'
  counter = getColumnsNumber(dbfile)-3
  if res == counter:
    counter += 1
    new_column += str(counter)

    c.execute("ALTER TABLE dbase ADD COLUMN '{cn}' TEXT".format(cn=new_column))
  else:
    new_column += str(res+1)

  query_note = 'UPDATE dbase SET ' + new_column + '=?' + ' WHERE login=?'
  query_cnt = 'UPDATE dbase SET counter' + '=?' + ' WHERE login=?'
  c.execute(query_note, (str(note), login))
  c.execute(query_cnt, (res+1, login))

  conn.commit()
  conn.close()

def getNotesFromDatabase(dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('SELECT * FROM dbase')
  allData = c.fetchall()

  notes = {}
  for user in allData:
    c.execute('SELECT counter FROM dbase WHERE login=?', (str(user[0]), ))
    res = c.fetchall()[0][0]
    notes[user[0]] = []

    if res == 0:
      continue
    for i in range(res):
      notes[user[0]].append(user[3+i])

  print notes
  conn.commit()
  conn.close()
  return notes

def getColumnsNumber(dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('SELECT * FROM dbase')
  allData = c.fetchall()

  conn.commit()
  conn.close()
  return len(allData[0])

def hashPassword(password):
  return pbkdf2_sha256.encrypt(str(password), rounds=2000, salt_size=16)
