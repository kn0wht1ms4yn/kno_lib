## `from kno import requests`
- NOTE: Don't try to use this in any type of a production application.  It is very simple code made for hackers by hackers.
- Send WYSIWYG HTTP requests sent with raw `sockets` rather then `urllib`.
- Works with either HTTP or HTTPS.
- I was inspired to build this tool after using the Python `requests` library to test for path traversal during a web app security audit.  The problem is that when you send a request using the Python `requests` library then the resulting request that gets sent is not necesarrily what you want.  For example, a path with `../` in it will get normalized and removed.  This is because Python `requests` uses `urllib` behind the scenes which does the normalization.  You can get around this with url encoding like `%2e%2e%2f` which gets past `urllib` normalization.  Then `requests` url decodes the path into `../` and then url encodes it again.  `../` persits through the url encode because it contains url-safe characters.  The point is that there's too much going on for someone conductig a pen test that just wants to be 100% sure of the request that is being sent.
### requests.get(url, headers={}, body='', verify=True)
- Send an HTTP GET request.
- Headers can be specified like `{ 'Content-Type': 'application/json' }`
- The **body** paramter accepts a raw string.  For example, if you want the body to contain JSON then you must use something like `json.dumps()`
- The **verify** paramter specifies whether or not 
```
>>> requests.get('http://someHost.com/index.html')
'HTTP/1.1 200 OK\r\naccess-control-allow-origin: *\r\ncontent-type: text/html; charset=utf-8\r\ncontent-length: 28\r\nconnection: close\r\ndate: Mon, 04 May 2026 19:33:23 GMT\r\n\r\nMeow meow, index.html, meow.'
```
### requests.post(url, data=None, json=None, headers={}, verify=True)
- Send an HTTP POST request.
- The **data** and **json** parameters both expect a `dict` and are mutually exclusive.  If a **data** argument is provided then the request will be sent with a `Content-Type: application/x-www-form-urlencoded` header.  If a **json** argument is provided then the request will be sent with a `Content-Type: application/json` header.  This behavior is similar to the Python `requests` library.
- The **verify** paramter specifies whether or not 
```
>>> requests.post('http://someHost.com/index.html', data={ 'someKey': 'someVal' })
'HTTP/1.1 200 OK\r\naccess-control-allow-origin: *\r\ncontent-type: text/html; charset=utf-8\r\ncontent-length: 28\r\nconnection: close\r\ndate: Mon, 04 May 2026 20:02:04 GMT\r\n\r\nMeow meow, index.html, meow.'
```