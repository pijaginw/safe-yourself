import sqlite3
import uuid

# token jest aktualnie wyslany na strone
def tokenIsBeingUsed(dbfile, token):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('UPDATE tokens SET isBeingUsed=? WHERE token=?', (1, str(token)))
  conn.commit()
  conn.close()

def isTokenBeingUsed(dbfile, token):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('SELECT isBeingUsed FROM tokens WHERE token=?', (str(token), ))
  res = c.fetchall()

  if len(res) > 0:
    if res[0][0] == 0:
      return False
  return True 

# token zostal zwrocony przez strone
def tokenIsUsed(dbfile, token):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('SELECT used FROM tokens WHERE token=?', (str(token), ))
  res = c.fetchall()

  if len(res) > 0:
    print res
    if res[0][0] == 0:
      print 'token jest poprawny'
      c.execute('UPDATE tokens SET used=? WHERE token=?', (1, str(token)))
      conn.commit()
      conn.close()
      return True
    else:
      print '\ntoken nie jest poprawny'
  return False

def createTokens(dbfile):
  for i in range(15):
    token = str(uuid.uuid4())
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('INSERT INTO tokens (token) VALUES (?)', (str(token), ))

    conn.commit()
    conn.close()

def getTokenFromDatabase(dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('SELECT * FROM tokens')
  allTokens = c.fetchall()

  res = ''
  for t in allTokens:
    if isTokenBeingUsed(dbfile, t) is False:
      res = t[0]

  if res == '':
    c.execute('UPDATE tokens SET used=0')
    conn.commit()
    for t in allTokens:
      if t[1] == 0:
        res = t[0]
  conn.close()
  return str(res)
