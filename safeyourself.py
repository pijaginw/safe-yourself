# -*- coding: utf-8 -*-
from vial import Vial, render_template
import sqlite3
import cgi
from passlib.hash import pbkdf2_sha256

dbFile = '/home/pijaginw/safeyourself/safe-yourself/dbase.db'

notes = {}
session = {}


def index(headers, body, data):
  return 'Hello', 200, {}

def login(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('login.html', body=body, data=data), 200, {}
    
  elif request_method == 'POST':
    login = cgi.escape(str(data['inputLogin']), quote=True)
    password = cgi.escape(str(data['inputPass']), quote=True)

    if isUserInDatabase(login, dbFile) is False:
      return 'there is no such a user!', 200, {}

    if isPasswordCorrect(login, password, dbFile) is True:
      global session
      session['user'] = login
      session['ip'] = headers['remote-addr']
      print session
      
      if login not in notes:
        notes[login] = []
      return render_template('notes.html', body=body, data=data, notes=notes), 200, {}

    elif isPasswordCorrect(login, password, dbFile) is False:
      return 'error: password is not correct!', 200, {}

def addToDatabase(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('INSERT INTO dbase VALUES (?, ?)', (login, hashPassword(password)))
  conn.commit()
  conn.close()
  notes[login] = []
  print notes

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
      return render_template('login.html', body=body, data=data), 200, {}


def hashPassword(password):
  return pbkdf2_sha256.encrypt(str(password), rounds=2000, salt_size=16)


def postNote(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('notes.html', body=body, data=data, 
                            notes=notes, username=session['user']), 200, {}

  elif (request_method == 'POST' and ('user' in session)):
    note = cgi.escape(str(data['noteTextarea']), quote=True)
    #addNoteToDatabase(note, login, dbFile)
    addNote(session['user'], str(note))
    print notes
    return render_template('notes.html', body=body, data=data, 
                            notes=notes, username=session['user']), 200, {}
    
def addNote(login, note):
  if login not in notes:
    return 'wrong user !!', 200, {}
  else:
    notes[login].append(note)

"""def addNoteToDatabase(note, login, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('INSERT INTO dbase (note) WHERE login=? VALUES (?)', (login, str(note)))
  conn.commit()
  conn.close()"""

def changePass(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('settings.html', body=body, data=data, 
                            username=session['user']), 200, {}

  elif request_method == 'POST':
    oldpass = cgi.escape(str(data['oldPass']), quote=True)
    newpass = cgi.escape(str(data['newPass']), quote=True)
    newpass2 = cgi.escape(str(data['newPass2']), quote=True)

    if isPasswordCorrect(session['user'], oldpass, dbFile):
      newpass = cgi.escape(str(data['newPass']), quote=True)
      newpass2 = cgi.escape(str(data['newPass2']), quote=True)
      changePassword(session['user'], newpass, dbFile)

      return render_template('login.html', body=body, data=data), 200, {}

def changePassword(login, newpass, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('UPDATE dbase SET password=? WHERE login=?', 
                          (hashPassword(newpass), login))
  conn.commit()
  conn.close()
  

def logout(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    global session
    session = {}
    return render_template('login.html', body=body, data=data), 200, {}

routes = {
  '/': index,
  '/login': login,
  '/signup': signup,
  '/notes': postNote,
  '/settings': changePass,
  '/logout': logout,
}

app = Vial(routes, prefix='/pijaginw/safeyourself', static='/static').wsgi_app()

