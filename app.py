
from flask import Flask, render_template
from flask_socketio import SocketIO , send , Namespace ,join_room, leave_room
from users import *
from threading import Timer

import json

# join room  without being in the talking queue yet. 
# leave room
# permission to talk  
# stop talking (should be already in his turn to talk) 

# TODO implement avatar for each user, it will be just a string representing the name of the avatar.




# necessary startup code 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
# declared lists to be used as long as the server is up.
Rooms = dict()


if __name__ == '__main__':
    socketio.run(app)    




@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message , broadcast=True)
    


@socketio.on("CreateRoom")
def create_room(data):
    newRoom = Room(data["room"])
    newUser = User(data["username"])
    Rooms[newRoom.name] = newRoom
    #addUser assigns a new id for the user and maps it to the name and returns the assigned id back to the user to use
    AssignedID = newRoom.addUser(newUser)
    print("created room with name :",newRoom.name)
    join_room(newRoom.name)
    print("{0} joined room".format(data["username"]))
    send(newUser.name + ' has entered the room.', room=newRoom.name)
    return AssignedID

@socketio.on("JoinRoom")
def add_user_to_room(data):
    choosenRoom = Rooms[data["room"]]
    userObject = User(data["username"])
    AssignedID = choosenRoom.addUser(userObject)
    join_room(data["room"])
    print("{0} has joined the room".format(data["username"]))
    send(data["username"] + ' has entered the room.',room= data["room"])
    tempChoosenRoom = choosenRoom
    tempChoosenRoom.talkerThread=''
    message = {
        "AssignedID": AssignedID,
        "Room" : json.dumps(tempChoosenRoom.__dict__),
    }
    return message




# TODO impelemnt leaving the queue
@socketio.on("LeaveRoom")
def remove_user_from_room(data):
    leave_room(data["room"])
    send(data["username"] + ' has left the room.',room= data["room"])


def nextUser(roomName):
    print(roomName)
    room = Rooms[roomName]
    message = {
        "type": "userStoppedSpeaking",
        "userName": room.talker,
    }
    with app.test_request_context('/'):
        socketio.send(message, room=roomName)
    # send(message,room = roomName)
    room.talker = ''

    if len(room.queue)>0:
        UserToTalk = room.queue[0].name
        userToTalkID = room.queue[0].id
        del room.queue[0]
        room.talker = UserToTalk
        queueTimer = Timer(10 , nextUser,{roomName : roomName})
        queueTimer.start()

        print("{0} started talking for 10 secs".format(room.talker))
        message = {
            "type": "userStartedSpeaking",
            "userID": userToTalkID,
            "username": UserToTalk
        }
        socketio.send(message,room= roomName)
        room.talkerThread = queueTimer
    else:
        return

# TODO implement adding users to the queue
@socketio.on("JoinQueue")
def JoinQueue(data):
    roomName = data["room"]
    room=Rooms[roomName]
    
    #Whenever there is no one in
    if len(room.queue)==0 and room.talker =='':
        room.talker = data["username"]
        queueTimer = Timer(10,nextUser,{roomName : roomName})
        print("{0} started talking for 10 secs".format(room.talker))
        queueTimer.start()

        message = {
            "type": "userStartedSpeaking",
            "userID": data["userID"],
            "username":data["username"]
        }
        send(message,room=data["room"])
        room.talkerThread = queueTimer
    else:
        userObject = User(data["username"])
        userObject.setID(data["userID"])
        room.queue.append(userObject)
        message = {
            "type": "userJoinsQueue",
            "userID": userObject.id,
            "username":userObject.name
        }
        send(message, room=data["room"])
        print("{0} is added to queue".format(data["username"]))


@socketio.on("LeaveQueue")
def leaveQueue(data):
    userObject = User(data["username"])
    userObject.setID(data["userid"])
    message = {
        "type":"userLeavesQueue",
        "userID": userObject.id,
        "username":userObject.name
    }
    socketio.send(message,json=True, room = data["room"])


@socketio.on("StopTalking")
def StopTalking(data):
    roomName = data["room"]
    choosenRoom = Rooms[roomName]
    choosenRoom.talkerThread.cancel()
    nextUser(roomName)
    message = {
        "type":"userStopTalking"
    }
    socketio.send(message,json=True, room = roomName)

# @socketio.on("LeaveQueue")
# def JoinQueue(data):

# @socketio.on("StopTaking")
# def StopTaking(data)
@socketio.on("GetRooms")
def GetRoomsList():
    roomNames = list()
    for key , value in Rooms.items():
        roomNames.append(value.name)
    return roomNames

@app.route("/")
def return_available_rooms():
    return "hello world, i'm deployed"  