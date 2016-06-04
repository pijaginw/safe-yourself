# -*- coding: utf-8 -*-
from vial import Vial, render_template

def index(headers, body, data):
  return 'Hello', 200, {}

def hello(headers, body, data, name):
  return 'Howdy ' + name, 200, {}

def login(headers, body, data):
  request_method = headers['request-method']
  if request_method == 'GET':
    return render_template('login.html', body=body, data=data), 200, {}
  elif request_method == 'POST':
    return 'login POST', 200, {}

def upload(headers, body, data):
  return render_template('upload.html', body=body, data=data), 200, {}

routes = {
  '/': index,
  '/login': login,
  '/hello/{name}': hello,
  '/upload': upload,
}

app = Vial(routes, prefix='/pijaginw/safeyourself', static='/static').wsgi_app()

