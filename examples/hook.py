from celeryhooks.models import Listener
from celeryhooks.hooks import Hook

class MyHook(Hook):
    name = "myhook"



def install_listener():
    l = Listener(url="http://localhost:8000/celeryhooks/debug/",
             hook=MyHook.name)
    l.save()
    
