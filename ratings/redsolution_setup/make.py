from redsolutioncms.make import BaseMake
from redsolutioncms.models import CMSSettings
from os.path import dirname, join

class Make(BaseMake):

    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()

        cms_settings.render_to('settings.py', 'settings.pyt', {  
        })
        cms_settings.render_to('urls.py', 'urls.pyt', {   
        })

make = Make()