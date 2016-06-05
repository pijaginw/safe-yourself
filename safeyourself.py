# -*- coding: utf-8 -*-
from vial import Vial, render_template
import sqlite3

dbFile = '/home/pijaginw/safeyourself/safe-yourself/dbase.db'
logged_in = False


def index(headers, body, data):
  return 'Hello', 200, {}

def login(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('login.html', body=body, data=data), 200, {}
    
  elif request_method == 'POST':
    login = data['inputLogin']
    password = data['inputPass']

    if isUserInDatabase(login, dbFile) is False:
      addToDatabase(login, password, dbFile)
      return render_template('login.html', body=body, data=data), 200, {}

    if isPasswordCorrect(login, password, dbFile) is True:
      logged_in = True
      return 'password is correct - user has logged in', 200, {}

    elif isPasswordCorrect(login, password, dbFile) is False:
      logged_in = False
      return 'error: password is not correct!', 200, {}

def addToDatabase(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('INSERT INTO dbase VALUES (?, ?)', (str(login), str(password)))
  conn.commit()
  conn.close()

def isUserInDatabase(login, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('SELECT * FROM dbase WHERE login=?', (str(login), ))
  conn.commit()
  result = c.fetchall()
  conn.close()

  if len(result) == 0:
    return False
  print 'i have found that user\n'
  return True

def isPasswordCorrect(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('SELECT password FROM dbase WHERE login=?', (str(login), ))
  conn.commit()
  result = c.fetchall()
  conn.close()

  if str(result[0][0]) == str(password):
    return True
  return False


routes = {
  '/': index,
  '/login': login,
}

app = Vial(routes, prefix='/pijaginw/safeyourself', static='/static').wsgi_app()

