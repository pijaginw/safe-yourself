# -*- coding: utf-8 -*-
from vial import Vial, render_template, to_ascii, to_unicode
from databaseactivities import *
from tokens import *
import math
import json
import time
import unicodedata
import string
import cgi

dbFile = '/home/pijaginw/safeyourself/safe-yourself/dbase.db'
session = {}
fails = {}
areTokensCreated = False

allowedCharacters = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e',
                      'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
                      'u','v','w','x','y','z','A','B','C','D','E','F','G','H','I',
                      'J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X',
                      'Y','Z','!','"','#','$','%','&',"'",'(',')','*','+',',','.',
                      '-','/',':',';','=','?','@','[','\\',']','^','_','`','{','|','}','~']

def index(headers, body, data):
  if headers['request-method'] == 'GET':
    createTokens(dbFile)
    areTokensCreated = True
    
    t = getTokenFromDatabase(dbFile)
    print t
    tokenIsBeingUsed(dbFile, t)
    return render_template('login.html', body=body, data=data, token=t), 200, {}
  else:
    msg = ''
    return render_template('error.html', body=body, data=data, msg=msg), 405, {}

def login(headers, body, data):
  request_method = headers['request-method']
  global areTokensCreated
  if areTokensCreated is False:
    createTokens(dbFile)
    areTokensCreated = True

  if request_method == 'GET':
    print '\nget w login'
    t = getTokenFromDatabase(dbFile)
    print t
    tokenIsBeingUsed(dbFile, t)
    return render_template('login.html', body=body, data=data, token=t), 200, {}
    
  elif request_method == 'POST':
    if 'secretIn' in data:
      print '\npost w login ----> otrzymalem token'
      print data['secretIn']
      if tokenIsUsed(dbFile, data['secretIn']) is False:
        msg = 'You are a hacker.'
        return render_template('error.html', msg=msg), 400, {}

    if len(data) < 2:
      msg = 'All fields must be filled.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    l = cgi.escape(str(data['inputLogin']), quote=True) 
    p = cgi.escape(str(data['inputPass']), quote=True)

    login = ''.join(ch for ch in l if ch.isalnum())
    password = ''.join(ch for ch in p if ch in allowedCharacters)

    if isUserInDatabase(login, dbFile) is False:
      msg = 'Invalid login.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    if isPasswordCorrect(login, password, dbFile) is True:
      global session
      session['user'] = login
      session['ip'] = headers['remote-addr']
      fails[headers['remote-addr']] = 0
      print '-----'
      print session
      print fails
      print '-----'

      notes = getNotesFromDatabase(dbFile)
      t = getTokenFromDatabase(dbFile)
      tokenIsBeingUsed(dbFile, t)
      return render_template('notes.html', body=body, data=data, notes=notes, token=t), 200, {}

    elif isPasswordCorrect(login, password, dbFile) is False:

      if headers['remote-addr'] in fails:
        fails[headers['remote-addr']] += 1
        if fails[headers['remote-addr']] > 3:
          time.sleep(2)
          fails[headers['remote-addr']] = 0
          return render_template('login.html', body=body, data=data, token=t), 200, {}
        else:
          msg = 'Invalid password.'
          return render_template('error.html', body=body, data=data, msg=msg), 400, {}
      else:
        fails[headers['remote-addr']] = 1
        msg = 'Invalid password.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

def signup(headers, body, data):
  request_method = headers['request-method']
  global areTokensCreated
  if areTokensCreated is False:
      createTokens(dbFile)
      areTokensCreated = True

  if request_method == 'GET':
    t = getTokenFromDatabase(dbFile)
    tokenIsBeingUsed(dbFile, t)
    print t
    print '\nget w signup'
    return render_template('signup.html', body=body, data=data, token=t), 200, {}

  elif request_method == 'POST':
    if 'secretIn' in data:
      print 'post w signup --> secret\n'
      print data['secretIn']
      if tokenIsUsed(dbFile, data['secretIn']) is False:
        msg = 'You are a hacker.'
        return render_template('error.html', msg=msg), 400, {}

    if len(data) < 3:
      msg = 'All fields must be filled.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    l = cgi.escape(str(data['inputLogin']), quote=True)
    p = cgi.escape(str(data['inputPass']), quote=True)
    p2 = cgi.escape(str(data['inputPass2']), quote=True)

    login = ''.join(ch for ch in l if ch.isalnum())
    password = ''.join(ch for ch in p if ch in allowedCharacters)
    password2 = ''.join(ch for ch in p2 if ch in allowedCharacters)

    if isUserInDatabase(login, dbFile) is True:
      msg = 'Invalid login.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    if password != password2:
      msg = 'Invalid password.'
      return render_template('error.html', body=body, data=data, msg=msg), 400, {}

    else:
      addToDatabase(login, password, dbFile)
      t = getTokenFromDatabase(dbFile)
      print t
      tokenIsBeingUsed(dbFile, t)
      return render_template('login.html', body=body, data=data, token=t), 200, {}

def postNote(headers, body, data):
  request_method = headers['request-method']

  global areTokensCreated
  if areTokensCreated is False:
      createTokens(dbFile)
      areTokensCreated = True

  global session
  if ('user' in session) and (headers['remote-addr'] == session['ip']):

    if request_method == 'GET':
      print '\nget w notes '
      t = getTokenFromDatabase(dbFile)
      print t
      tokenIsBeingUsed(dbFile, t)
      notes = getNotesFromDatabase(dbFile)

      return render_template('notes.html', body=body, data=data, 
                              notes=notes, username=session['user'], token=t), 200, {}

    elif request_method == 'POST':
      if 'secretIn' in data:
        print '\npost w notes ----> otrzymalem token'
        print data['secretIn']
        if tokenIsUsed(dbFile, data['secretIn']) is False:
          msg = 'You are a hacker.'
          return render_template('error.html', msg=msg), 400, {}

      if len(data) == 0:
        msg = 'You can\'t post an empty note.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

      note = cgi.escape(str(data['noteTextarea']), quote=True)

      try:
        addNoteToDatabase(note, session['user'], dbFile)
      except Exception, e:
        print '\nthere is sth fishy going on. %s\n' % str(e)
        return render_template('error.html', body=body, data=data), 500, {}

      notes = getNotesFromDatabase(dbFile)
      print notes

      t = getTokenFromDatabase(dbFile)
      print t
      tokenIsBeingUsed(dbFile, t)
      return render_template('notes.html', body=body, data=data, 
                              notes=notes, username=session['user'], token=t), 200, {}

  else:
    session = {}
    t = getTokenFromDatabase(dbFile)
    print t
    tokenIsBeingUsed(dbFile, t)
    return render_template('login.html', body=body, data=data, token=t), 200, {}

def changePass(headers, body, data):
  request_method = headers['request-method']

  global areTokensCreated
  if areTokensCreated is False:
      createTokens(dbFile)
      areTokensCreated = True

  global session
  if ('user' in session) and (headers['remote-addr'] == session['ip']):

    if request_method == 'GET':
      print 'get w change pass'
      t = getTokenFromDatabase(dbFile)
      print t
      tokenIsBeingUsed(dbFile, t)
      return render_template('settings.html', body=body, data=data, 
                              username=session['user'], token=t), 200, {}

    elif request_method == 'POST':
      if 'secretIn' in data:
        print 'post w notes ----> otrzymalem token'
        print data['secretIn']
        if tokenIsUsed(dbFile, data['secretIn']) is False:
          msg = 'You are a hacker.'
          return render_template('error.html', msg=msg), 400, {}

      if len(data) < 3: # <--------------------------------------------------------------------- to do ????
        msg = 'All fields must be filled.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

      oldpass = cgi.escape(str(data['oldPass']), quote=True)

      if isPasswordCorrect(session['user'], oldpass, dbFile):
        newpass = cgi.escape(str(data['newPass']), quote=True)
        newpass2 = cgi.escape(str(data['newPass2']), quote=True)

        changePassword(session['user'], newpass, dbFile)

        session = {}
        t = getTokenFromDatabase(dbFile)
        print t
        tokenIsBeingUsed(dbFile, t)
        return render_template('login.html', body=body, data=data, token=t), 200, {}
      else:
        msg = 'Invalid password.'
        return render_template('error.html', body=body, data=data, msg=msg), 400, {}

  else:
    session = {}
    t = getTokenFromDatabase(dbFile)
    print t
    tokenIsBeingUsed(dbFile, t)
    return render_template('login.html', body=body, data=data, token=t), 200, {}

def logout(headers, body, data):
  request_method = headers['request-method']

  if request_method == 'GET':
    global session
    session = {}
    t = getTokenFromDatabase(dbFile)
    return render_template('login.html', body=body, data=data, token=t), 200, {}

def validation(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'POST':
    if 'pass' in data:
      password = cgi.escape((str(data['pass'])), quote=True)

      if entropy(str(password)) > 2.2:
        response = {'value': 'OK'}
        return json.dumps(response), 200, {'content-type': 'application/json'}
      else:
        response = {'value': 'WRONG'}
        return json.dumps(response), 200, {'content-type': 'application/json'}

    response = {'value': 'WRONG'}
    return json.dumps(response), 200, {'content-type': 'application/json'}

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

