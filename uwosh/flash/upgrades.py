from Products.CMFCore.utils import getToolByName
from uwosh.flash.content.interfaces import IMultimedia
from HTMLParser import HTMLParser, HTMLParseError
from urlparse import urlsplit, urlunsplit
from Acquisition import aq_parent
from Products.Archetypes.Field import TextField
from urllib import unquote
from ZODB.POSException import ConflictError
from OFS.interfaces import IItem
from OFS.Image import Image
from Products.Archetypes.Widget import RichWidget

class LinkParser(HTMLParser):
    """ a simple html parser for link and image urls """

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def getLinks(self):
        """ return all links found during parsing """
        return tuple(self.links)

    def handle_starttag(self, tag, attrs):
        """ override the method to remember all links """
        if tag == 'img':
            self.links.extend(search_attr('src', attrs))


def search_attr(name, attrs):
    """ search named attribute in a list of attributes """
    for attr, value in attrs:
        if attr == name:
            return [value]
    return []


def extractLinks(data):
    """ parse the given html and return all links """
    parser = LinkParser()
    try:
        parser.feed(data)
        parser.close()
    except HTMLParseError:
        pass
    return parser.getLinks()


def findObject(base, path):
    """ traverse to given path and find the upmost object """
    obj = base
    components = path.split('/')
    while components:
        child_id = unquote(components[0])
        try:
            child = obj.restrictedTraverse(child_id)
        except ConflictError:
            raise
        except:
            return None, None
        if not IItem.providedBy(child):
            break
        obj = child
        components.pop(0)
    return obj, '/'.join(components)


def getObjectsFromLinks(base, links):
    """ determine actual objects refered to by given links """
    objects = set()
    url = base.absolute_url()
    scheme, host, path, query, frag = urlsplit(url)
    site = urlunsplit((scheme, host, '', '', ''))
    for link in links:
        s, h, path, q, f = urlsplit(link)
        if (not s and not h) or (s == scheme and h == host):    # relative or local url
            obj, extra = findObject(base, path)
            if obj:
                if IMultimedia.providedBy(obj):
                    objects.add((link, obj))
                elif isinstance(obj, Image):
                    obj = aq_parent(obj)    # use atimage object for scaled images
                    if IMultimedia.providedBy(obj):
                        objects.add((link, obj))

    return objects


def upgrade_to_0_7rc2(context):
    """ perform upgrade to 0.7rc2 -- Some important changes. """
    portal_catalog = getToolByName(context, 'portal_catalog')
    
    multimedia = portal_catalog.searchResults(object_provides=IMultimedia.__identifier__)
    
    for media in multimedia:
        obj = media.getObject()
        obj.reindexObject(idxs=['info'])
        if hasattr(obj, 'streaming_url'):
            # all of them will be flv since that is all that 
            # we supported at first
            setattr(obj, 'original_content_type', 'video/x-flv')
            
    # Now go through all content and see if they have multimedia embedded
    # in them. If they do, we need to rewrite the url.
    all_brains = portal_catalog.searchResults()
    for brain in all_brains:
        obj = brain.getObject()
        for field in obj.Schema().fields():
            if isinstance(field, TextField) and isinstance(field.widget, RichWidget):
                accessor = field.getAccessor(obj)
                text = accessor()
                links = extractLinks(text)
                res = getObjectsFromLinks(obj, links)
            
                for link, media in res:
                    link = link.replace('&', '&amp;') # somewhere the &amp; is replaced with & and we don't want this.
                    new_link = link.split('?')[0] + "?" + media.info()
                    new_link = new_link.replace('++resource++flash.png', 'flashimage').replace('&', '&amp;')
                    text = text.replace(link, new_link)
                    field.set(obj, text)
                    
                if len(res) > 0:
                    obj.reindexObject()
                
    #reload javascript to make new version of flash.js available
    portal_javascripts = getToolByName(context, 'portal_javascripts')
    portal_javascripts.cookResources()
    

    
def upgrade_to_0_7(context):
    #reload javascript to make new version of flash.js available
    portal_javascripts = getToolByName(context, 'portal_javascripts')
    portal_javascripts.cookResources()