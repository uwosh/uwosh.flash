from Products.CMFCore.utils import getToolByName
from config import accepted_media_types

def multimedia_edited(multimedia, event):
    """
    change the id of a multimedia object when the file changes.
    Otherwise, you can't know the file type when trying to decide how to handle the media type.
    """
    pass
    #current_id = multimedia.getId()
    #file_object = multimedia.getField('file').getRaw(multimedia)
    #filename = file_object.filename

    #if filename != current_id:
    #    putils = getToolByName(multimedia, 'plone_utils')
        #multimedia.setId(putils.normalizeString(filename))
        #multimedia.setTitle(putils.normalizeString(filename))
    