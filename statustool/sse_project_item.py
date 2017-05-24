__author__ = 'jshen'
__version__ = '1.0'


class ProjectItem:
    def __init__(self, item_name):
        self.name = item_name

    def __init__(self, item_name, item_detail):
        self.name = item_name
        self.detail = item_detail

    def get_name(self):
        return self.name

    def get_detail(self):
        return self.detail