from config import default_content_types

def get_content_type(fi):
    """
    
    >>> class FakeFile(object):
    ...   filename = None
    ...   content_type = None
    ...   def __init__(self, filename, content_type):
    ...     self.filename = filename
    ...     self.headers = {'content-type' : content_type}
    
    >>> from uwosh.flash.utils import get_content_type
    >>> fi = FakeFile('something.swf', 'application/x-shockwave-flash')
    >>> get_content_type(fi)
    'application/x-shockwave-flash'
    
    >>> fi = FakeFile('something.swf', 'application/octet-stream')
    >>> get_content_type(fi)
    'application/x-shockwave-flash'
    
    >>> fi = FakeFile('something.flv', 'application/octet-stream')
    >>> get_content_type(fi)
    'video/x-flv'
    
    >>> fi = FakeFile('something.mp3', 'application/octet-stream')
    >>> get_content_type(fi)
    'audio/mp3'
    
    """
    
    content_type = fi.headers.get('content-type', '')
    
    if content_type == 'application/octet-stream':
        filename = fi.filename
        file_ext = filename[filename.rfind('.')+1:].lower()
        if file_ext in default_content_types.keys():
            return default_content_types[file_ext]
            
    return content_type