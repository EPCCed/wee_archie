import abc

#Abstract Data transfer object class.
#Note that each demo MUST define its own subclass of this class (in *demo_name*_demo.py), and define its own vesion of each of the methods
class AbstractDTO:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def SetData():
        return
        
    @abc.abstractmethod
    def GetData():
        return 

