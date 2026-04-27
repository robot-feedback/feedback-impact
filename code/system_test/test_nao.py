import naoqi
from naoqi import ALProxy

SAM = "192.168.1.128"
ROBOT_IP = SAM
PORT = 9559
tts = ALProxy("ALTextToSpeech",ROBOT_IP, PORT)

tts.say("Hello, world!")
tts.setParameter("speed", 10)

message= "I'm working fine! Thanks for checking me."
message_str = "\\style=didactic\\ \\vol=90\\ \\wait=5\\" + message
tts.say(message_str)