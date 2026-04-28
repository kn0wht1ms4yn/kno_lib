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
import socket, ssl, re
import json as json_lib
from .exceptions import MultipleRequestContentType, InvalidProto, InvalidUrl
from .constants import DEFAULT_HEADERS, ALLOWED_PROTO

class Request:
    def __init__(self, method, url, headers={}, body='', verify=True):
        '''
            method = str
            url = str
            headers = dict
            body = str
        '''
        self.method = method
        self.url = url
        self.headers = DEFAULT_HEADERS
        self.headers.update(headers)
        self.body = body
        self.proto, self.host, self.port, self.path = self.parse_url()
        self.verify = verify

    def __str__(self):
        return self.build()

    def parse_url(self):
        '''
            Convert from a string like `http://www.meow.com:80/a/b/c?d=e#f` to a dict
            like `{ proto, host, path }`.  Path will always include query and fragment
            because this purpose of this library is to have control over the request,
            not necessarily creating a 'proper' request.
        '''
        url = self.url
        pattern = r'^(.*?)://(.*?)(?::(.*?))?/(.*?)$'
        found = re.findall(pattern, url)
        if len(found) > 1:
            raise(InvalidUrl)
        proto, host, port, path = found[0]

        if not proto or not host:
            raise(InvalidUrl)
        if proto not in ALLOWED_PROTO:
            raise(InvalidProto)

        path = '/' + path
        port_map = {
            'http': 80,
            'https': 443
        }
        if not port:
            port = port_map[proto]
        else:
            port = int(port)

        return (proto, host, port, path)

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
        method = self.method
        headers = self.build_headers()
        body = self.body
        host = self.host
        path = self.path

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
        proto = self.proto
        host = self.host
        port = 80 if proto == 'http' else 443
        verify = self.verify
        req = self.build_request()

        with socket.create_connection((host, port)) as s:
            if proto == 'http':
                s.send(req.encode())
                resp = b''
                while c := s.recv(1024):
                    resp += c
            elif proto == 'https':
                context = ssl.create_default_context()
                if not verify:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                with context.wrap_socket(s, server_hostname=host) as ssl_s:
                    ssl_s.send(req.encode())
                    resp = b''
                    while c := ssl_s.recv(1024):
                        resp += c
            else:
                raise(InvalidProto)
        
        return resp.decode()

class Response:
    pass

def generic_send(method, url, headers, body, verify=True):
    '''
        Function to format a generic request, send it, and return the response.
    '''
    req = Request(method, url, headers, body, verify)
    resp = req.send()
    return resp

def get(url, headers={}, body='', verify=True):
    '''
        QOL function to format a GET request.
    '''
    resp = generic_send('GET', url, headers, body, verify)
    return resp

def post(url, data=None, json=None, headers={}, verify=True):
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
    
    resp = generic_send('POST', url, headers, body, verify)
    return resp
