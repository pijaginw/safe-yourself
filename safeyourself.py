# -*- coding: utf-8 -*-
from vial import Vial, render_template
import sqlite3
import cgi
from passlib.hash import pbkdf2_sha256
import math
import json
import uuid

dbFile = '/home/pijaginw/safeyourself/safe-yourself/dbase.db'

#notes = {}
session = {}
counter = 0
cookie = 0

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

      #if login not in notes:
      #  notes[login] = []
      notes = getNotesFromDatabase(dbFile)
      return render_template('notes.html', body=body, data=data, notes=notes), 200, {}

    elif isPasswordCorrect(login, password, dbFile) is False:
      return 'error: password is not correct!', 200, {}

def addToDatabase(login, password, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('INSERT INTO dbase (login, password) VALUES (?, ?)', (login, hashPassword(password)))
  conn.commit()
  conn.close()
  #notes[login] = []
  #print notes

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
      print entropy(password)
      
      return render_template('login.html', body=body, data=data), 200, {}


def hashPassword(password):
  return pbkdf2_sha256.encrypt(str(password), rounds=2000, salt_size=16)


def postNote(headers, body, data):
  request_method = headers['request-method']

  if request_method == 'GET':
    notes = getNotesFromDatabase(dbFile)
    return render_template('notes.html', body=body, data=data, 
                            notes=notes, username=session['user']), 200, {}

  elif (request_method == 'POST' and ('user' in session)):
    note = cgi.escape(str(data['noteTextarea']), quote=True)
    addNoteToDatabase(str(note), session['user'], dbFile)
    #addNote(session['user'], str(note))

    #global notes
    notes = getNotesFromDatabase(dbFile)
    print notes
    return render_template('notes.html', body=body, data=data, 
                            notes=notes, username=session['user']), 200, {}
    
# def addNote(login, note):
#   if login not in notes:
#     return 'wrong user !!', 200, {}
#   else:
#     notes[login].append(note)

def addNoteToDatabase(note, login, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('SELECT counter FROM dbase WHERE login=?', (str(login), ))
  conn.commit()
  res = c.fetchall()

  if len(res) == 1:
    res = res[0][0]
    print res

  new_column = 'note'
  global counter
  if res == counter:
    counter += 1
    new_column += str(counter)

    c.execute("ALTER TABLE dbase ADD COLUMN '{cn}' TEXT".format(cn=new_column))
  else:
    new_column += str(res+1)

  print new_column

  c.execute("UPDATE dbase SET '{cn}'='{note}' WHERE login='{lg}'".format(cn=new_column, note=str(note), lg=login))
  c.execute("UPDATE dbase SET '{cn}'='{c}' WHERE login='{lg}'".format(cn='counter', c=res+1, lg=login))

  conn.commit()
  conn.close()

def changePass(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('settings.html', body=body, data=data, 
                            username=session['user']), 200, {}

  elif request_method == 'POST':
    oldpass = cgi.escape(str(data['oldPass']), quote=True)
    #newpass = cgi.escape(str(data['newPass']), quote=True)
    #newpass2 = cgi.escape(str(data['newPass2']), quote=True)

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


def validation(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'POST':
    password = cgi.escape((body), quote=True)
    response = {'entropy': entropy(str(password))}
  return json.dumps(response), 200, {'content-type': 'application/json'}


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


def entropy(password):
  res = 0
  chars = {}
  
  for ch in password:
    if ch not in chars:
      chars[ch] = 1
    else:
      chars[ch] += 1

  for i in chars:
    l = float(len(password))
    res += (chars[i]/l)*math.log(chars[i]/l, 2)

  return -res







routes = {
  '/': index,
  '/login': login,
  '/signup': signup,
  '/notes': postNote,
  '/settings': changePass,
  '/logout': logout,
  '/signup/validation': validation,
}

app = Vial(routes, prefix='/pijaginw/safeyourself', static='/static').wsgi_app()

