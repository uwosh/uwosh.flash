from Products.Archetypes.Field import FileField, StringField, ObjectField
from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.layer import ILayerContainer
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from ftplib import FTP
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from Products.Archetypes.Storage import AttributeStorage
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.Widget import FileWidget
from uwosh.flash.config import FLASH_MEDIA_SERVER_CONFIG as flash_conf
from uwosh.flash.config import max_file_size
from utils import get_content_type

class FTPServerStorageDelegate:
    """
    
    >>> from uwosh.flash import fields 
    >>> fields.aq_base = lambda x : x
    
    >>> class FakeInstance(object):
    ...   _p_changed = None
    ...   streaming_url = None
    ...   original_content_type = None

    >>> class FakeFile(object):
    ...   filename = None
    ...   content_type = None
    ...   def __init__(self, filename, content_type):
    ...     self.filename = filename
    ...     self.headers = {'content-type' : content_type}
    
    >>> class FakeFTP(object):
    ...   login = lambda s, x, y : None
    ...   cwd = lambda s, x : None
    ...   set_pasv = lambda s, x : None
    ...   mkd = lambda s, x : None
    ...   nlst = lambda s : ['one', 'two']
    ...   storbinary = lambda s, x, y : None
    ...   def __init__(s, add): return s
    >>> fields.FTP = FakeFTP
    
    >>> class FakeField(object):
    ...   unset = lambda s, x : None
    
    >>> fields.FTPServerStorageDelegate.unset = lambda s, i : None
    
    >>> class FakePUtils(object):
    ...   normalizeString = lambda s, x : x
    ...   getPortalObject = lambda s : None
    >>> fields.getToolByName = lambda x, y : FakePUtils()
    
    >>> fi = FakeFile('something.mp3', 'application/octet-stream')
    >>> instance = FakeInstance()
    >>> fields.FTPServerStorageDelegate(FakeField()).set(instance, fi)
    >>> instance.streaming_url != None
    True
    >>> instance.original_content_type
    'audio/mp3'
    
    >>> fi = FakeFile('something.flv', 'application/octet-stream')
    >>> instance = FakeInstance()
    >>> fields.FTPServerStorageDelegate(FakeField()).set(instance, fi)
    >>> instance.streaming_url != None
    True
    >>> instance.original_content_type
    'video/x-flv'
    
    >>> fi = FakeFile('something.flv', 'video/x-flv')
    >>> instance = FakeInstance()
    >>> fields.FTPServerStorageDelegate(FakeField()).set(instance, fi)
    >>> instance.streaming_url != None
    True
    >>> instance.original_content_type
    'video/x-flv'
    
    """
    
    
    def __init__(self, field):
        self.field = field
        
    def set(self, instance, value, **kwargs):
        #just in case they have old file around
        self.field.unset(instance, **kwargs)
        
        putils = getToolByName(instance, 'plone_utils')
        portal = getToolByName(instance, "portal_url").getPortalObject()
        storage_directory = putils.normalizeString(getattr(instance, 'title', 'no-title'))

        ftp = FTP(flash_conf.ftp_address)
        ftp.login(flash_conf.ftp_user, flash_conf.ftp_password)
        ftp.cwd(flash_conf.ftp_media_directory)
        ftp.set_pasv(flash_conf.ftp_use_passive_mode)
        
        if storage_directory not in ftp.nlst():
            ftp.mkd(storage_directory)
        
        ftp.cwd(storage_directory)
        
        media_list = ftp.nlst()
        has_media_set = True
        folder = current_media = False
        filename = value.filename
        if hasattr(instance, 'streaming_url') and getattr(instance, 'streaming_url', None):
            folder, current_media = getattr(instance, 'streaming_url').split("/")
        else:
            has_media_set = False
         
        #check if already has a file set
        if has_media_set:
            #always just delete the old file...
            if folder == storage_directory and current_media in media_list:
                ftp.delete(current_media)
                media_list.remove(current_media)
            
        #check if video of same name exists on server already
        new_filename = filename
        count = 1
        while new_filename in media_list:
            new_filename = filename[:-4] + "-" + str(count) + "." + filename[-3:]
            count += 1
        
        ftp.storbinary("STOR %s" % new_filename, value)
        
        setattr(aq_base(instance), 'streaming_url', storage_directory + "/" + new_filename)
        setattr(aq_base(instance), 'original_content_type', get_content_type(value))
        instance._p_changed = 1 #this is what makes the change persistant
        
    
class MultimediaWidget(FileWidget):
    _properties = FileWidget._properties.copy()
    _properties.update({
        'macro' : "multimediawidget",
        'show_content_type' : True,
        })

    security = ClassSecurityInfo()
    

class MultimediaField(FileField):
    """
    to handle uploading to flash streaming media server
    """
    
    implements(IFileField, ILayerContainer)
    
    _properties = FileField._properties.copy()
    
    _properties.update({
        'widget' : MultimediaWidget,
        'streaming_url_storage' : AttributeStorage(),
        'maxsize' : max_file_size
    })
    
    security  = ClassSecurityInfo()
        
    def __init__(self, name=None, **kwargs):
        FileField.__init__(self, name, **kwargs)
        
        # eventually support multiple storage mechanisms
        # will need to dynamically choose what one to use
        self.storage_delegate = FTPServerStorageDelegate(self)
        
    security.declarePrivate('usesStreamingServer')
    def usesStreamingServer(self):
        return flash_conf and hasattr(flash_conf, 'server_address') and \
            hasattr(flash_conf, 'ftp_address') and hasattr(flash_conf, 'ftp_user') and \
            hasattr(flash_conf, 'ftp_password') and hasattr(flash_conf, 'ftp_media_directory')
        
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Assign input value to object. If mimetype is not specified,
        pass to processing method without one and add mimetype returned
        to kwargs. Assign kwargs to instance.
        
        need to check to see if we should store on streaming server or
        in plone
        
        """
        
        # for some reason archetypes calls this method multiple times on
        # an install..  This just makes the base class handle the save when
        # nothing is present so I don't have to deal with it.
        if not value:
            return super(MultimediaField, self).set(instance, value, **kwargs)
            
        #if swf, just do old way
        if value.headers.get('content-type', None) == 'application/x-shockwave-flash' or not self.usesStreamingServer():
            try:
                delattr(aq_base(instance), 'streaming_url')
                delattr(aq_base(instance), 'original_content_type')
            except AttributeError:
                pass
            instance._p_changed = 1
            return super(MultimediaField, self).set(instance, value, **kwargs)
        else:
            return self.storage_delegate.set(instance, value, **kwargs) 
        
        
