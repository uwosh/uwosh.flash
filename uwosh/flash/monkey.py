#
# MONKEY PATCHING
# Yes, I know this is bad....
# 


# Need to do this one so you can get more info from
# kupu when adding multimedia
# 
# 
# Might be better to eventually create a transform
# that performs the replacement client side
# that would be SWEET

from Products.kupu.plone import plonedrawers
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

old_method = plonedrawers.InfoAdaptor.info

def new_info(self, brain, allowLink=True):
    res = old_method(self, brain, allowLink)

    if brain.portal_type == 'Multimedia':
        res['url'] = res['url'] + '?' + brain.info
    
    return res

plonedrawers.InfoAdaptor.info = new_info
