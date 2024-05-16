import datetime

class Package:
    def __init__(self,dID, dAddress, dDeadline : datetime.datetime.time, dStatus, dTime):
        self.dID = dID
        self.dAddress = dAddress
        self.dDeadline = dDeadline
        self.dStatus = dStatus
        self.dTime = dTime