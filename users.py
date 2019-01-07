
class Room:

    def __init__(self, name ):
        self.name = name
        self.queue = list()
        self.talker = ''
        self.talkerThread = ''
        self.userID_map_Username = dict()
        self.Last_ID_value=0

    
    def addUser(self , user):
        self.userID_map_Username[self.Last_ID_value] = user.name
        user.setID(self.Last_ID_value)
        self.Last_ID_value +=1
        #the user's ID
        return self.Last_ID_value -1
  

class User:
    def __init__(self , name):
        self.name = name
        self.avatar = ''
        self.id = ''

    def setID(self,id):
        self.id = id


