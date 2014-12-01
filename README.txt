Introduction
============
uwosh.flash offers people a way of inserting flash into plone in a safe manner. This way you do not have to worry about turning off safe html and adding accepted tags to kupu. You do, however, have to require javascript to do this.

Right now it can be connected to a flash streaming server to serve FLV video files and MP3 audio files.

You must use uwosh.recipe.flash to connect it with a streaming server!


Upgrade Notes for 0.7rc2
------------------------

* After you install the product, you MUST run the upgrade step in order for the flash streaming video to function properly from there on out. Flash video should still work as expected.

* While running the upgrade script, it might be a good idea to idea to run it on a zope that isn't being used much because it does a good deal of work for converting links and reindexing objects.

* DO NOT just reinstall the product to do the upgrade. This will not actually upgrade it! 
    
* Plone 3.3
    
    * site setup -> add/remove products -> click upgrade button
    
* Plone 3.2 and Plone 3.1

    * zmi -> portal_setup -> Uprades -> choose uwosh.flash -> Upgrade to 0.7rc2
    
