import zmq
import naoqi
from naoqi import ALProxy


SAM = "192.168.1.128"
ROBOT_IP = SAM
PORT = 9559
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555") 

tts = ALProxy("ALAnimatedSpeech",ROBOT_IP, PORT)
# tts = ALProxy("ALTextToSpeech",ROBOT_IP, PORT)


while True:
    message = socket.recv_string()
    print("Received message: {}".format(message))
    message_str = message.encode('utf-8')
    # print("Encoded message type: {}".format(type(message_str)))
    message_str = "\\style=didactic\\ \\vol=90\\ \\wait=5\\" + message_str
    tts.say(message_str)
    socket.send_string("Message received by NAO")
