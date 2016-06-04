# -*- coding: utf-8 -*-
from io import BytesIO
from cgi import FieldStorage
from parse import parse
from jinja2 import Template
from os.path import isfile
from mimetypes import guess_type

STATUS_CODE = {
    200: '200 OK',
    201: '201 Created',
    301: '301 Moved Permanently',
    303: '303 See Other',
    304: '304 Not Modified',
    400: '400 Bad Request',
    401: '401 Unauthorized',
    403: '403 Forbidden',
    404: '404 Not Found',
    405: '405 Method Not Allowed',
    409: '409 Conflict',
    500: '500 Internal Server Error',
    501: '501 Not Implemented',
}

def to_ascii(s):
    return s.encode('utf-8')

def to_unicode(s):
    for codec in ['utf-8', 'iso-8859-1']:
        try:
            return s.decode(codec)
        except UnicodeError, e:
            continue
    print u"Couldn't find the correct codec. Decoded using 'UTF-8'."
    print u"Ignored non-UTF-8 characters. Sorry."
    return s.decode('utf-8', errors='ignore')

def serve_static(headers, body, data, filepath):
    if headers['request-method'] not in ['GET', 'HEAD']:
        return 'Only GET/HEAD methods allowed for static resources', 405, {}
    filepath = '.' + filepath
    if not isfile(filepath):
        return 'File "%s" does not exist' % filepath, 404, {}
    try:
        f = open(filepath, 'rb')
    except IOError, e:
        return 'File "%s" is not readable' % filepath, 403, {}
    content = to_unicode(f.read())
    content_type, _ = guess_type(filepath)
    return content, 200, {'Content-Type' : content_type or 'text/plain'}

def not_found(headers, body, data, uri, prefix):
    return 'Could not find a handler for URI %s (prefix: %s)' \
         % (uri, prefix), 404, {}

def render_template(template_filename, **kwargs):
    with open(template_filename, 'r') as f:
        template_content = to_unicode(f.read())
        template = Template(template_content)
    return template.render(**kwargs)

class FormTextField(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return to_unicode(self.value)

class FormFileField(object):
    def __init__(self, filename, headers, stream):
        self.filename = filename
        self.headers = headers
        self.stream = stream

    def __getattr__(self, name):
        if name is 'value':
            self.stream.seek(0) # Rewind the file to the beggining
            return self.stream.read()
        raise AttributeError, name

    def __repr__(self):
        content = self.stream.read(10) + '...'
        return to_unicode('FormFile(filename="%s", value="%s")' % (self.filename, content))

class Vial(object):
    def __init__(self, routes, prefix=None, static=None, before=None):
        self.routes = routes
        self.prefix = prefix
        self.static = static
        self.before = before

    def get_request(self, environ):
        uri = environ['REQUEST_URI']
        body = environ['wsgi.input'].read()
        headers = {
            'content-length': environ.get('CONTENT_LENGTH', 0),
            'request-method': environ.get('REQUEST_METHOD', None),
            'content-type': environ.get('CONTENT_TYPE', 'text/html'),
            'remote-addr': environ.get('REMOTE_ADDR', None),
            'request-uri': environ.get('REQUEST_URI', None),
            'http-accept': environ.get('HTTP_ACCEPT', None),
            'http-host': environ.get('HTTP_HOST', None),
            'http-accept-language': environ.get('HTTP_ACCEPT_LANGUAGE', None),
            'http-accept-encoding': environ.get('HTTP_ACCEPT_ENCODING', None),
            'http-x-forwarded-for': environ.get('HTTP_X_FORWARDED_FOR', None),
        }
        if uri.startswith(self.prefix):
            uri = uri.replace(self.prefix, '', 1)
        return headers, body, uri

    def get_before_handler(self):
        if self.before is not None:
            return self.before
        return lambda headers: None
           
    def get_handler(self, uri):
        # static routes
        if uri.startswith(self.static):
            return serve_static, {'filepath': uri}
        # regular routes
        for uri_template, handler in self.routes.iteritems():
            args = parse(uri_template, uri)
            if args is not None:
                args = args.named
            if args is not None:
                return handler, args
        # missing route
        return not_found, {'uri': uri, 'prefix': self.prefix}

    def get_data(self, body, headers, environ):
        fields = FieldStorage(fp=BytesIO(body), headers=headers, environ=environ)
        if len(fields.value) is 0:
            return {}

        data = {}
        for name in fields:
            field = fields[name]
            if field.filename is not None:
               data[name] = FormFileField(field.filename, field.headers, field.file)
            else:
               data[name] = FormTextField(field.value)

        return data

    def wsgi_app(self):
        def app(environ, start_response):
            request_headers, request_body, uri = self.get_request(environ)
            before_handler = self.get_before_handler()
            handler, args = self.get_handler(uri)
            # Values in data are extracted from the RAW request body.
            data = self.get_data(request_body, request_headers, environ)
            def make_response(response):
               body, status_code, headers = response
               # WSGI expects headers as a list of tuples
               # but it is easier to return them from handler
               # as a dictionary, so I am rewriting it here
               headers = [(h, v) for h, v in headers.iteritems()]
               status = STATUS_CODE.get(status_code)
               start_response(status, headers)
               return [to_ascii(body)]
            # Jinja2 expects Unicode strings, so to make request_body
            # ready to render, we decode it as unicode.
            # Check the implementation of to_unicode, as it tries
            # few popular codecs, but if nothing works it decodes it
            # IGNORING non-representable characters.
            request_body_as_unicode = to_unicode(request_body)
            response = before_handler(request_headers)
            if response is not None:
                return make_response(response)
            response = handler(request_headers, request_body_as_unicode, data, **args)
            return make_response(response)
        return app
