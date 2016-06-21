# -*- coding: utf-8 -*-
from vial import Vial, render_template, to_ascii, to_unicode
import sqlite3
import cgi
from passlib.hash import pbkdf2_sha256
import math
import json
import time

dbFile = '/home/pijaginw/safeyourself/safe-yourself/dbase.db'
session = {}
fails = {}

def login(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('login.html', body=body, data=data), 200, {}
    
  elif request_method == 'POST':
    if len(data) < 2:
      msg = 'All fields must be filled.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    login = cgi.escape(str(data['inputLogin']), quote=True)
    password = cgi.escape(str(data['inputPass']), quote=True)

    if isUserInDatabase(login, dbFile) is False:
      msg = 'Invalid login.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    if isPasswordCorrect(login, password, dbFile) is True:
      global session
      session['user'] = login
      session['ip'] = headers['remote-addr']
      print session

      notes = getNotesFromDatabase(dbFile)
      return render_template('notes.html', body=body, data=data, notes=notes), 200, {}

    elif isPasswordCorrect(login, password, dbFile) is False:
      global fails
      if login in fails:
        fails[login] += 1
        if fails[login] > 3:
          time.sleep(10)
          fails[login] = 0
          return render_template('login.html', body=body, data=data), 200, {}
        else:
          msg = 'Invalid password.'
          return render_template('error.html', body=body, data=data, msg=msg), 400, {}
      else:
        fails[login] = 1
        msg = 'Invalid password.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

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

def signup(headers, body, data):
  request_method = headers['request-method']

  if request_method == 'GET':
    return render_template('signup.html', body=body, data=data), 200, {}

  elif request_method == 'POST':
    if len(data) < 3:
      msg = 'All fields must be filled.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    login = cgi.escape(str(data['inputLogin']), quote=True)
    password = cgi.escape(str(data['inputPass']), quote=True)
    password2 = cgi.escape(str(data['inputPass2']), quote=True)


    if password != password2:
      msg = 'Invalid password.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    else:
      addToDatabase(login, password, dbFile)
      return render_template('login.html', body=body, data=data), 200, {}


def hashPassword(password):
  return pbkdf2_sha256.encrypt(str(password), rounds=2000, salt_size=16)


def postNote(headers, body, data):
  request_method = headers['request-method']

  if 'user' in session: # czy uzytkownik jest zalogowany?
    if headers['remote-addr'] == session['ip']: # czy jest to ta sama sesja?

      if request_method == 'GET':
        notes = getNotesFromDatabase(dbFile)
        return render_template('notes.html', body=body, data=data, 
                                notes=notes, username=session['user']), 200, {}

      elif request_method == 'POST':
        try:
          if len(data) == 0:
            msg = 'You can\'t post an empty note.'
            return render_template('error.html', body=body, data=data, msg=msg), 400, {}
          n = to_unicode(str(data['noteTextarea']))
          note = cgi.escape(n, quote=True)

          try:
            addNoteToDatabase(note, session['user'], dbFile)
          except Exception, e:
            return render_template('error.html', body=body, data=data), 500, {}

          notes = getNotesFromDatabase(dbFile)
          print notes
          return render_template('notes.html', body=body, data=data, 
                                  notes=notes, username=session['user']), 200, {}

        except Exception, e:
          return render_template('error.html', body=body, data=data), 500, {}

    else:
      global session
      session = {}
      return render_template('login.html', body=body, data=data), 200, {}
  else:
    global session
    session = {}
    return render_template('login.html', body=body, data=data), 200, {}

def addNoteToDatabase(note, login, dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('SELECT counter FROM dbase WHERE login=?', (str(login), ))
  conn.commit()
  res = c.fetchall()

  if len(res) == 1:
    res = res[0][0]

  new_column = 'note'
  counter = getColumnsNumber(dbFile)-3
  if res == counter:
    counter += 1
    new_column += str(counter)

    c.execute("ALTER TABLE dbase ADD COLUMN '{cn}' TEXT".format(cn=new_column))
  else:
    new_column += str(res+1)

  c.execute("UPDATE dbase SET '{cn}'='{note}' WHERE login='{lg}'".format(cn=new_column, note=str(note), lg=login))
  c.execute("UPDATE dbase SET '{cn}'='{c}' WHERE login='{lg}'".format(cn='counter', c=res+1, lg=login))
  # c.execute("UPDATE dbase SET ?=? WHERE login=?", (str(new_column), str(note), str(login)))
  # c.execute("UPDATE dbase SET ?=? WHERE login=?", ('counter', res+1, str(login)))

  #c.execute("SELECT Count(*) FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{db}'".format(db='dbase'))
  #print c.fetchall()
  conn.commit()
  conn.close()

def changePass(headers, body, data):
  request_method = headers['request-method']

  if ('user' in session) and (headers['remote-addr'] == session['ip']):
    if request_method == 'GET':
      return render_template('settings.html', body=body, data=data, 
                              username=session['user']), 200, {}

    elif request_method == 'POST':    
      if len(data) == 0:
        msg = 'You have to enter your old password in order to set a new one.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

      oldpass = cgi.escape(str(data['oldPass']), quote=True)

      if isPasswordCorrect(session['user'], oldpass, dbFile):
        if len(data) < 3:
          msg = 'All fields must be filled.'
          return render_template('error.html', body=body, data=data, msg=msg), 400, {}

        newpass = cgi.escape(str(data['newPass']), quote=True)
        newpass2 = cgi.escape(str(data['newPass2']), quote=True)

        changePassword(session['user'], newpass, dbFile)
        global session
        session = {}
        return render_template('login.html', body=body, data=data), 200, {}
      else:
        msg = 'Invalid password.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

  else:
    global session
    session = {}
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

def getColumnsNumber(dbfile):
  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('SELECT * FROM dbase')
  allData = c.fetchall()

  conn.commit()
  conn.close()
  return len(allData[0])


routes = {
  '/login': login,
  '/signup': signup,
  '/notes': postNote,
  '/settings': changePass,
  '/logout': logout,
  '/signup/validation': validation,
}

app = Vial(routes, prefix='/pijaginw/safeyourself', static='/static').wsgi_app()

