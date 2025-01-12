from base64 import b64encode, b64decode
from io import BytesIO
import itertools
import collections
import sys

try:
    # Python 3
    from urllib.parse import urlencode

    def convert_str(s):
        """Convert bytes to str, if required"""
        return s.decode('utf-8') if isinstance(s, bytes) else s

    def convert_byte(b):
        """Convert str to bytes, if required"""
        return b.encode('utf-8', errors='strict') if isinstance(b, str) else b

except ImportError:
    # Python 2
    from urllib import urlencode

    def convert_str(s):
        """No conversion required for Python 2"""
        return s

    def convert_byte(b):
        """Convert str to bytes, if required"""
        return b.encode('utf-8', errors='strict') if isinstance(b, str) else b

__all__ = ['response']


def convert_b46(s):
    """Base64 encode the given string"""
    return b64encode(s).decode('ascii')


class StartResponse(object):
    def __init__(self, base64_content_types=None):
        self.status = 500
        self.status_line = '500 Internal Server Error'
        self.headers = []
        self.chunks = collections.deque()
        self.base64_content_types = set(base64_content_types or []) or set()

    def __call__(self, status, headers, exc_info=None):
        self.status_line = status
        self.status = int(status.split()[0])
        self.headers[:] = headers
        return self.chunks.append

    def use_binary_response(self, headers, body):
        content_type = headers.get('Content-Type')
        if content_type and ';' in content_type:
            content_type = content_type.split(';')[0]
        return content_type in self.base64_content_types

    def build_body(self, headers, output):
        totalbody = b''.join(itertools.chain(self.chunks, output))
        is_b64 = self.use_binary_response(headers, totalbody)

        converted_output = convert_b46(totalbody) if is_b64 else convert_str(totalbody)
        return {
            'isBase64Encoded': is_b64,
            'body': converted_output,
        }

    def response(self, output):
        headers = dict(self.headers)
        rv = {
            'statusCode': self.status,
            'headers': headers,
        }
        rv.update(self.build_body(headers, output))
        return rv


class StartResponse_GW(StartResponse):
    def response(self, output):
        rv = super(StartResponse_GW, self).response(output)
        rv['statusCode'] = str(rv['statusCode'])
        return rv


class StartResponse_ELB(StartResponse):
    def response(self, output):
        rv = super(StartResponse_ELB, self).response(output)
        rv['statusCode'] = int(rv['statusCode'])
        rv['statusDescription'] = self.status_line
        return rv


def environ(event, context):
    """Convert Lambda event to WSGI environment"""
    body = event.get('body', '') or ''
    if event.get('isBase64Encoded', False):
        body = b64decode(body)

    body = convert_byte(body)
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),  # Default to GET if missing
        'SCRIPT_NAME': '',
        'SERVER_NAME': '',
        'SERVER_PORT': '',
        'PATH_INFO': event.get('path', '/'),  # Default to root path if missing
        'QUERY_STRING': urlencode(event.get('queryStringParameters') or {}),
        'REMOTE_ADDR': '127.0.0.1',
        'CONTENT_LENGTH': str(len(body)),
        'HTTP': 'on',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.input': BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.url_scheme': '',
        'awsgi.event': event,
        'awsgi.context': context,
    }

    headers = event.get('headers', {}) or {}
    for k, v in headers.items():
        k = k.upper().replace('-', '_')

        if k == 'CONTENT_TYPE':
            environ['CONTENT_TYPE'] = v
        elif k == 'HOST':
            environ['SERVER_NAME'] = v
        elif k == 'X_FORWARDED_FOR':
            environ['REMOTE_ADDR'] = v.split(', ')[0]
        elif k == 'X_FORWARDED_PROTO':
            environ['wsgi.url_scheme'] = v
        elif k == 'X_FORWARDED_PORT':
            environ['SERVER_PORT'] = v

        environ['HTTP_' + k] = v

    return environ


def select_impl(event, context):
    if 'elb' in event.get('requestContext', {}):
        return environ, StartResponse_ELB
    else:
        return environ, StartResponse_GW


def response(app, event, context, base64_content_types=None):
    """Main function to handle Lambda and WSGI interaction"""
    environ_func, StartResponse = select_impl(event, context)
    sr = StartResponse(base64_content_types=base64_content_types)
    output = app(environ_func(event, context), sr)
    return sr.response(output)
