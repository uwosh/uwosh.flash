from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize
from uwosh.flash.config import STREAMING_OPTIONS
from datetime import datetime
from struct import pack
import time
from cStringIO import StringIO
from Acquisition import aq_inner
from uwosh.flash.config import FLASH_MEDIA_SERVER_CONFIG as flash_conf

class View(BrowserView):
    
    template = ViewPageTemplateFile('multimedia.pt')

    def __call__(self):
        return self.template()
        
    def server_address(self):
        if hasattr(flash_conf, 'server_address'):
            return flash_conf.server_address.rstrip("/")
        else:
            return ""
        
    def flv_address(self):
        if hasattr(self.context, 'streaming_url'):
            return getattr(self.context, 'streaming_url').rstrip(".flv")
        else:
            return None
            
            
class DownloadMedia(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        field = context.getField('file')
        file_object = field.getRaw(context)

        self.request.response.setHeader('Content-Disposition', 'inline; filename=%s' % field.getFilename(context))
        self.request.response.setHeader("Content-Length", file_object.get_size())
        self.request.response.setHeader('Content-Type', file_object.getContentType())
        file = field.get(context, raw=True)
        return file.index_html(self.request, self.request.response)
            
    
class FlashImage(BrowserView):
    """
    used to choose what image to show as a placeholder
    for the flash element
    """
    def __call__(self):
        if self.context.getBackgroundImage():
            self.request.response.redirect('backgroundImage_large')
        else:
            self.request.response.redirect('++resource++flash.png')
        
 
OPTIONS = {
    'interval' : {
        'low' : 1,
        'medium' : .5,
        'high' : .3
    },
    'size' : {
        'low' : 10,
        'medium': 40,
        'high' : 90
    }
}
                
class Stream(BrowserView):
    """
    As far as I know, this will only work with flowplayer
    This is a copy of a similar thing done with php here http://richbellamy.com/wiki/Flowplayer_streamer_php
    We're not even using this right now.  Maybe allow some way to enable it????  Or use when they do not have a 
    streaming server set up.
    """
    
    def __call__(self):
        """
        
        """
        context = aq_inner(self.context)
        file_object = context.getField('file').getRaw(context)
        
        try:
            # For blobs
            fi = file_object.getIterator()
        except AttributeError:
            fi = StringIO(str(file_object.data))

        seek_position = int(self.request.get(STREAMING_OPTIONS['get_position'], 0))

        packet_interval = OPTIONS['interval'][self.request.get('bw', STREAMING_OPTIONS['default_speed'])]
        packet_size = OPTIONS['size'][self.request.get('bw', STREAMING_OPTIONS['default_speed'])] * 1042 
        
        file_size = file_object.get_size()

        if seek_position > 0:
            file_size = file_size - seek_position + 1
            
        if not STREAMING_OPTIONS['allow_file_cache']:
            #prevent caching...
            self.request.response.setHeader('Expires', 'Thu, 19 Nov 1981 08:52:00 GMT')
            self.request.response.setHeader("Last-Modified",  "%s GMT" % datetime.now().strftime("%a, %b %m %Y %H:%M:%S")) # no need to have?
            self.request.response.setHeader("Cache-Control", "max-age=0, private, must-revalidate, post-check=0, pre-check=0")
            self.request.response.setHeader("Pragma", "no-cache")

        self.request.response.setHeader("Content-Type", "video/x-flv")
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % file_object.filename)
        self.request.response.setHeader("Content-Length", file_size)

        if seek_position != 0:
            self.request.response.stdout.write("FLV\x01\x01\0\0\0\x09\0\0\0\x09")
        
        fi.seek(seek_position)
        
        data = "throw_away"

        while len(data) > 0:
            
            if STREAMING_OPTIONS['limit_bandwidth']:
            
                st = datetime.now()

                data = fi.read(packet_size)

                self.request.response.stdout.write(data)
            
                et = datetime.now()

                diff = float((st - et).microseconds)/1000000
		
                if diff < packet_interval:
                    time.sleep(packet_interval - diff)
            else:
                data = fi.read(file_size)
                self.request.response.write(data)        