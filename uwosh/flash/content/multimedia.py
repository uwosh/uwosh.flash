from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes import ATCTMessageFactory as _
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from uwosh.flash.config import accepted_content_types, max_file_size, \
    PRODUCT_NAME, content_type_mapping
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.ATContentTypes.content.base import ATCTFileContent
from validators import IsFileExtension
from Products.validation import V_REQUIRED
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.image import ATCTImageTransform
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.utils import getToolByName
from uwosh.flash.fields import MultimediaField, MultimediaWidget
from uwosh.flash.config import FLASH_MEDIA_SERVER_CONFIG as flash_conf
from urllib import urlencode
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

copied_fields = {}


copied_fields['title'] = ATContentTypeSchema['title'].copy()
copied_fields['title'].required = True

schema = Schema((
    copied_fields['title'],
    
    MultimediaField('file',
        searchable=True,
        languageIndependent=True,
        validators = (
            ('isNonEmptyFile', V_REQUIRED),
            ('isMaxSize'),
            IsFileExtension("Is Media", content_types=accepted_content_types)
        ),
        widget = MultimediaWidget(
            description = 'You can upload SWF, MP3 and FLV file types.  '
                          'Max file size is %smb.' % (max_file_size),
            label=_(u'label_file', default=u'File'),
            show_content_type = False,
        )
    ),
    ImageField('backgroundImage',
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16)
        },
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkNewsImageMaxSize', V_REQUIRED)
        ),
        default=None,
        widget = ImageWidget(
            description = _(u'flash_default_image', 
                default=u'Image to be shown if flash is not supported and in visual editor. '),
            label= _(u'label_background_image', default=u'backgroundImage'),
            show_content_type = False
        )
    ),
    
    IntegerField('defaultWidth',
        required=False,
        default=400,
        widget=IntegerWidget(
            description = _(u'description_default_width', default=u'Width to use if one is not manually set in the visual editor.'),
            label = _(u'label_default_width', default=u'Default Width')
        )
    ),
    
    IntegerField('defaultHeight',
        required=False,
        default=300,
        widget=IntegerWidget(
            description = _(u'description_default_height', default=u'Height to use if one is not manually set in the visual editor.'),
            label = _(u'label_default_height', default=u'Default Height')
        )
    ),
    
    BooleanField('showSplashFrame',
        required=False,
        default=False,
        widget=BooleanWidget(
            description=_(u'description_showSplashFrame', default=u"Show the first frame of video as splash image."),
            title=_(u'label_showSplashFrame', default=u"Show Splash Frame?")
        )
    )
    
),
)


MultimediaSchema = ATContentTypeSchema.copy() + schema.copy()

finalizeATCTSchema(MultimediaSchema)

class Multimedia(ATCTContent, HistoryAwareMixin):
    """
    
    """
    
    assocMimetypes = ('application/*', 'video/*', 'audio/*')
    assocFileExt   = ('flv', 'swf', 'mp3')
    
    security = ClassSecurityInfo()

    implements(interfaces.IMultimedia)
    
    archetype_name = meta_type = portal_type = "Multimedia"
    _at_rename_after_creation = True

    schema = MultimediaSchema
    
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('backgroundImage'):
            field = self.getField('backgroundImage')
            image = None
            if name == 'backgroundImage':
                image = field.getScale(self)
            else:
                scalename = name[len('backgroundImage_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATCTContent.__bobo_traverse__(self, REQUEST, name)
    
    def uses_streaming_media(self):
        return hasattr(self, 'streaming_url')
    
    def streaming_server(self):
        if hasattr(flash_conf, 'server_address'):
            return flash_conf.server_address.rstrip('/')
        else:
            return 0
    
    def media_url(self):
        """
        this is the url that the flash streaming media server can consume.
        For FLV files it simply strips the file extension.
        For MP3 files it strips the file extension and adds mp3: before it.
        """
        
        if hasattr(flash_conf, 'server_address') and hasattr(self, 'streaming_url'):
            file_type = self.get_file_type()
            url = self.streaming_url[:self.streaming_url.rfind('.')]
            
            if file_type == 'mp3':
                url = 'mp3:%s' % url
            
            return url or 0
            
        else:
            return 0
    
    def get_file_type(self):
        if hasattr(self, 'original_content_type'):
            return content_type_mapping[self.original_content_type]
        elif self.uses_streaming_media():
            return hasattr(self, 'streaming_url') and \
                getattr(self, 'streaming_url')[-3:]
        else:
            try:
                filename = self.getFile().filename
                return filename[filename.rfind('.')+1:].lower()
            except:
                return 'unknown'
                
    
    def info(self):
        """
        info that can be set in the url of the image kupu uses for this
        """

        data = {
            'streaming_url': self.streaming_server(),
            'media_url': self.media_url(),
            'id': self.getId(),
            'width' : self.getDefaultWidth(),
            'height' : self.getDefaultHeight(),
            'file_type' : self.get_file_type(),
            'show_splash_frame' : str(self.getShowSplashFrame()).lower()
        }
        
        #if it isn't an flv, then just get the filename so we can know what to do with it
        if data['media_url'] == 0:
            file_obj = self.getField('file').getRaw(self)
            if type(file_obj) != str:
                data['filename'] = file_obj.filename
    
        return urlencode(data)
    
    
registerType(Multimedia, PRODUCT_NAME)