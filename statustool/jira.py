import base64
import json

__author__ = 'jshen'
__version__ = '1.0'

from statustool.restful_lib import Connection


class JiraInstance(object):
    def __init__(self, base_store_url, search_template, username=None, password=None, ):

        if base_store_url.endswith('/'):
            base_store_url = base_store_url[:-1]

        self.base_store_url = base_store_url
        self.json = None
        self.json_str = None
        self.username = username
        self.password = password
        self.search_template = search_template

        # Split the given URL
        if base_store_url:
            self.conn = Connection(base_store_url, username=username, password=password)

    def get_json_content(self, parameter_str):
        # Test to see if snapshot exists:
        request_path = self.search_template % parameter_str

        headers = {}
        headers["Authorization"] = "Basic {0}".format(base64.b64encode("{0}:{1}".format(self.username, self.password)))
        headers["content-type"] = "application/json"
        headers["accept"] = "application/json"
        resp = self.conn.request_get(request_path, args={}, headers=headers)
        headers = resp.get('headers')
        status = headers.get('status', headers.get('Status'))


        if status == '200' or status == '304':
            self.json_str = resp.get('body')
            self.json = json.loads(self.json_str, 'issues')
            return True
        else:
            print 'Error: %s - %s' % (headers.status, headers.reason)
            return False
