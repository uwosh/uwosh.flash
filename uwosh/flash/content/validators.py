from Products.validation.interfaces.IValidator import IValidator
from ZPublisher.HTTPRequest import FileUpload
from types import FileType
from uwosh.flash.utils import get_content_type
from Acquisition import *

class IsFileExtension:
    """Fails on empty non-existant files
    """

    __implements__ = IValidator

    def __init__(self, name, title='', description='', content_types=[]):
        self.name = name
        self.title = title or name
        self.description = description
        self.content_types = content_types

    def __call__(self, value, *args, **kwargs):
        
        content_type = get_content_type(value)

        if content_type in self.content_types:
            return True
        else:
            return ("Validation failed: You must use the correct type of file. "
                    "Accepted content types are %s. The content type you gave was %s" % 
                    (', '.join(self.content_types), value.headers.get('content-type'))
            )
