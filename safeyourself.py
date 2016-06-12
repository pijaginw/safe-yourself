# -*- coding: utf-8 -*-
from vial import Vial, render_template
import sqlite3
import cgi
from passlib.hash import pbkdf2_sha256

dbFile = '/home/pijaginw/safeyourself/safe-yourself/dbase.db'
logged_in = False


def index(headers, body, data):
  return 'Hello', 200, {}

def login(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('login.html', body=body, data=data), 200, {}
    
  elif request_method == 'POST':
    login = cgi.escape(str(data['inputLogin']), quote=True)
    password = cgi.escape(str(data['inputPass']), quote=True)
    print login
    print password

    if isUserInDatabase(login, dbFile) is False:
      return 'there is no such a user!', 200, {}

    if isPasswordCorrect(login, password, dbFile) is True:
      logged_in = True
      return 'password is correct - user has logged in', 200, {}

    elif isPasswordCorrect(login, password, dbFile) is False:
      logged_in = False
      return 'error: password is not correct!', 200, {}

def addToDatabase(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('INSERT INTO dbase VALUES (?, ?)', (login, hashPassword(password)))
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

  """hashPass = hashPassword(password)
  print "result= %s" % result
  print "hashPass= %s" % str(hashPass)
  print "password= %s" % str(password)
  return pbkdf2_sha256.verify(password, hashPass)"""
  return pbkdf2_sha256.verify(password, str(result[0][0]))

def signup(headers, body, data):
  request_method = headers['request-method']

  if request_method == 'GET':
    return render_template('signup.html', body=body, data=data), 200, {}

  elif request_method == 'POST':
    login = cgi.escape(str(data['inputLogin']), quote=True)
    password = cgi.escape(str(data['inputPass']), quote=True)
    password2 = cgi.escape(str(data['inputPass2']), quote=True)

    if password != password2:
      return 'error: repeated password is not correct!', 200, {}
    else:
      addToDatabase(login, password, dbFile)
      return 'new account has been successfully created', 200, {}


def hashPassword(password):
  return pbkdf2_sha256.encrypt(str(password), rounds=200000, salt_size=16)

routes = {
  '/': index,
  '/login': login,
  '/signup': signup,
}

app = Vial(routes, prefix='/pijaginw/safeyourself', static='/static').wsgi_app()

