__author__ = 'jshen'
__version__ = '1.0'

import mimetypes
import urllib
import urlparse
from cStringIO import StringIO

import httplib2

from statustool.mimeTypes import *


class Connection:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.username = username
        m = mimeTypes()
        self.mimetypes = m.getDictionary()
        
        self.url = urlparse.urlparse(base_url)
        
        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(base_url)
            
        self.scheme = scheme
        self.host = netloc
        self.path = path
        
        # Create Http class with support for Digest HTTP Authentication, if necessary
        self.h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
        self.h.follow_all_redirects = True
        if username and password:
            self.h.add_credentials(username, password)
    
    def request_get(self, resource, args = None, headers={}):
        return self.request(resource, "get", args, headers=headers)
        
    def request_delete(self, resource, args = None, headers={}):
        return self.request(resource, "delete", args, headers=headers)
        
    def request_head(self, resource, args = None, headers={}):
        return self.request(resource, "head", args, headers=headers)
        
    def request_post(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, "post", args , body = body, filename=filename, headers=headers)
        
    def request_put(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, "put", args , body = body, filename=filename, headers=headers)
        
    def get_content_type(self, filename):
        extension = filename.split('.')[-1]
        guessed_mimetype = self.mimetypes.get(extension, mimetypes.guess_type(filename)[0])
        return guessed_mimetype or 'application/octet-stream'

    def simple_request(self, url):
        resp, content = self.h.request(url)
        return resp, content

    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}):
        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'
        
        BOUNDARY = u'00hoYUXOnLD5RQ8SKGYVgLLt64jejnMwtO7q8XE1'
        CRLF = u'\r\n'
        
        if filename and body:
            #fn = open(filename ,'r')
            #chunks = fn.read()
            #fn.close()
            
            # Attempt to find the Mimetype
            content_type = self.get_content_type(filename)
            headers['Content-Type']='multipart/form-data; boundary='+BOUNDARY
            encode_string = StringIO()
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + CRLF)
            encode_string.write(u'Content-Disposition: form-data; name="file"; filename="%s"' % filename)
            encode_string.write(CRLF)
            encode_string.write(u'Content-Type: %s' % content_type + CRLF)
            encode_string.write(CRLF)
            encode_string.write(body)
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + u'--' + CRLF)
            
            body = encode_string.getvalue()
            headers['Content-Length'] = str(len(body))
        elif body:
            if not headers.get('Content-Type', None):
                headers['Content-Type']='text/xml'
            headers['Content-Length'] = str(len(body))        
        else:
            headers['Content-Type']='text/xml'
            
        if args:
            path += u"?" + urllib.urlencode(args)
            
        request_path = []
        if self.path != "/":
            if self.path.endswith('/'):
                request_path.append(self.path[:-1])
            else:
                request_path.append(self.path)
            if path.startswith('/'):
                request_path.append(path[1:])
            else:
                request_path.append(path)
        
        resp, content = self.h.request(u"%s://%s%s" % (self.scheme, self.host, u'/'.join(request_path)), method.upper(), body=body, headers=headers )
        
        return {u'headers':resp, u'body':content.decode('UTF-8')}
