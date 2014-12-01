from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
import logging
logger = logging.getLogger("uwosh.flash")

def import_various(context):
    
    if not context.readDataFile('uwosh.flash.txt'):
        return
        
    site = context.getSite()
    kupu = getToolByName(site, 'kupu_library_tool')
    site_props = getattr(getToolByName(site, 'portal_properties'), 'site_properties')
    
    types = kupu.getResourceType('mediaobject').get_portal_types()
    
    if 'Multimedia' not in types:
        types = types + ('Multimedia',)
        kupu.addResourceType('mediaobject', types)
        
    #add type info for File
    pa = kupu._preview_actions
    
    pa['Multimedia'] = {
        'classes' : ('flashElement',),
        'expression' : Expression("string:${object_url}/++resource++flashiconsmall.jpg"),
        'mediatype' : 'image',
        'defscale' : '',
        'scalefield': '',
        'normal': Expression("python: object_url + '/flashimage'")
    }
        
    kupu._preview_actions = pa
    
    #reindex all multimedia types incase something has changed in the way indexing is done
    pc = site.portal_catalog
    
    for mediaObj in pc.searchResults(portal_type="Multimedia"):
        try:
            mediaObj.getObject().reindexObject()
        except:
            logger.warn("caught exception reindexing '%s' at %s" % (mediaObj.id, mediaObj.getURL()))
