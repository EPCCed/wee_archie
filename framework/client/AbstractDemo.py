import abc

#define an abstract demo class which is the 'template' class for demo-specific code.
#Note that each demo MUST define its own subclass of this class (in *demo_name*_demo.py), and define its own vesion of each of the methods
class AbstractDemo(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def GetVTKData(self,root):
        return

    @abc.abstractmethod
    def RenderFrame(self,win,data):
        return


