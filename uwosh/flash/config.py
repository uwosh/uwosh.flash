DEPENDENCIES = [
]
PRODUCT_NAME = "uwosh.flash"

STREAMING_OPTIONS = {
    'limit_bandwidth': True,
    'allow_file_cache': True,
    'packet_size' : 90,
    'packet_interval' : 0.3,
    'allow_dynamic_bandwidth': True,
    'get_bandwidth' : 'bw',
    'default_speed' : 'high',
    'get_position': 'start'
}

accepted_content_types = (
    'application/x-shockwave-flash', 
    'application/futuresplash',
    
    'audio/mp3', 
    'audio/mpeg',
    'audio/x-mpeg',
    'audio/x-mp3',
    
    'video/x-flv', 
    'video/flv',
    'flv-application/octet-stream',
    'application/x-flash-video'
)

# map content type to file type
content_type_mapping = {
    
    'video/x-flv' : 'flv',
    'video/flv' : 'flv',
    'flv-application/octet-stream' : 'flv',
    'application/x-flash-video' : 'flv',
    
    'application/x-shockwave-flash' : 'swf',
    'application/futuresplash' : 'swf',
    
    'audio/mp3' : 'mp3',
    'audio/mpeg' : 'mp3',
    'audio/x-mpeg' : 'mp3',
    'audio/x-mp3' : 'mp3'
}

default_content_types = {
    'mp3' : 'audio/mp3',
    'flv' : 'video/x-flv',
    'swf' : 'application/x-shockwave-flash'
}

max_file_size = 100 #in mb
settings_file_name = 'plone-flashstreamingserver.conf'


from ZConfig.loader import ConfigLoader
from os import path
from Globals import INSTANCE_HOME

from ZConfig.datatypes import Registry
import ZConfig

_this_dir = path.dirname(path.abspath(__file__))
schema_file = path.join(_this_dir, "configschema.xml")
schema = ZConfig.loadSchema(schema_file)

try:
    FLASH_MEDIA_SERVER_CONFIG, hanlders = ZConfig.loadConfig(schema, path.join(INSTANCE_HOME, 'etc', settings_file_name))
except:
    FLASH_MEDIA_SERVER_CONFIG = {}
