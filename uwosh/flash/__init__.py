
from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils
ADD_CONTENT_PERMISSION = "Add portal content"
import monkey

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    import content

    content_types, constructors, ftis = atapi.process_types(atapi.listTypes('uwosh.flash'), 'uwosh.flash')

    cmfutils.ContentInit(
        'uwosh.flash Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)
        
        
        
