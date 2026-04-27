'''
    ! RULE #1: NOT FOR PRODUCTION
    ! RULE #2: DON'T USE IN PRODUCTION
    ! RULE #3: SEE RULES #1 and #2

    replicate the behavior of python requests library without urllib3
    - url as is, no encoding, decoding, encoding
    - never follow redirects
    - never verify

    requests.get('http://meow.com', headers={}, body='')
    requests.post('http://meow.com', headers={}, data={}, json={})
'''
import socket
import json as json_lib
from .exceptions import MultipleRequestContentType

DEFAULT_HEADERS = { 'User-Agent': 'kno requests 1.0' }

class Request:
    '''
        method = str
        url = str
        headers = dict
        body = str
    '''
    def __init__(self, method, url, headers={}, body=''):
        print('[Request] __init__')
        self.method = method
        self.url = url
        self.headers = DEFAULT_HEADERS
        self.headers.update(headers)
        self.body = body
        self.parsed_url = self.parse_url()

    def __str__(self):
        return self.build()

    def parse_url(self):
        '''
            Convert from a string like `http://www.meow.com/a/b/c?d=e#f` to a dict
            like `{ proto, host, path }`.  Path will always include query and fragment
            because this purpose of this library is to have control over the request,
            not necessarily creating a 'proper' request.
        '''
        url = self.url
        split = url.split('://', 1)
        proto = split[0]
        split = split[1].split('/', 1)
        host = split[0]
        path = '/' + split[1] if len(split)==2 else '/'

        url_dict = { 'proto': proto, 'host': host, 'path': path }
        return url_dict 

    def build_headers(self):
        '''
            Convert headers from a dict to a list of properly formatted header lines.
        '''
        body = self.body
        headers = []
        for k,v in self.headers.items():
            headers.append(f'{k}: {v}')
        if len(body):
            headers.append(f'Content-Length: {len(body)}')

        return headers

    def build_request(self):
        '''
            Combine method, path, headers, and body into a proper string with crlf ready to go on the wire.
        '''
        method = self.method.upper()
        headers = self.build_headers()
        body = self.body
        host = self.parsed_url['host']
        path = self.parsed_url['path']

        req = [
            f'{method} {path} HTTP/1.1',
            f'Host: {host}',
            *headers,
            'Connection: close'
        ]
        req = '\r\n'.join(req)
        req += '\r\n\r\n'
        req += body
        return req

    def send(self):
        '''
            Send the request and return the response.
        '''
        host = self.parsed_url['host']
        port = 80
        req = self.build_request()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(req.encode())

        resp = b''
        while c := s.recv(1024):
            resp += c
        
        return resp.decode()

class Response:
    pass

def generic_send(method, url, headers, body):
    '''
        Function to format a generic request, send it, and return the response.
    '''
    req = Request(method, url, headers, body)
    resp = req.send()
    return resp

def get(url, headers={}, body=''):
    '''
        QOL function to format a GET request.
    '''
    resp = generic_send('GET', url, headers, body)
    return resp

def post(url, data=None, json=None, headers={}):
    '''
        QOL function to format a POST request.
    '''
    # data and json params are mutually exclusive
    if data and json:
        raise(MultipleRequestContentType)
    
    if data:
        headers.update({ 'Content-Type': 'application/x-www-form-urlencoded' })
        body = []
        for k, v in data.items():
            body.append(f'{k}={v}')
        body = '&'.join(body)
    elif json:
        headers.update({ 'Content-Type': 'application/json' })
        body = json_lib.dumps(json)
    
    resp = generic_send('POST', url, headers, body)
    return resp
