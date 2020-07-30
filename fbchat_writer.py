import pyttsx3
import atexit
import json
import getpass
from fbchat import Client
from fbchat.models import *
import speech_recognition as sr
import os, re, sys, time

#Get password (this stable version of fbchat is stupid for requiring this regardless of whether cookies login works, but it works)
#password = getpass.getpass() #For live
password = 'PASSWORD' #For debugging 

def load_cookies(filename):
    try:
        # Load cookies from file
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        return  # No cookies yet

def save_cookies(filename, current_cookies):
    with open(filename, 'w') as f:
        json.dump(current_cookies, f)

cookies = load_cookies(os.path.join(sys.path[0], 'session.json'))
       
#Initiate client
writerClient = Client(getpass.getuser(), password, session_cookies=cookies)

#Save session cookies to file when the program exits
atexit.register(lambda: save_cookies(os.path.join(sys.path[0], 'session.json'), writerClient.getSession()))

run = True
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`            
        verbal_diarrhea = recognizer.recognize_google(audio, pfilter=0)
        if re.search('abracadabra', verbal_diarrhea):
            if(writerClient.searchForUsers(verbal_diarrhea.replace('abracadabra', ''))[0].is_friend==True):
                UID = writerClient.searchForUsers(verbal_diarrhea.replace('abracadabra', ''))[0].uid
                print("What to send to"+" "+writerClient.fetchUserInfo(UID)[UID].name)
                try: 
                    verbal_diarrhea = r.recognize_google(r.listen(m))
                except:
                    pass
            else:
                verbal_diarrhea = 'shazam' #stop
                print("Not friends")

        else:
            UID = writerClient.fetchThreadList(limit=1)[0].uid
        if (verbal_diarrhea.lower()!='shazam'):
            print("To", writerClient.fetchUserInfo(UID)[UID].name+":", verbal_diarrhea)
            writerClient.send(Message(text=verbal_diarrhea), thread_id=UID, thread_type=ThreadType.USER)
        else: 
            print("Nothing sent")
        
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)

while (run==True): time.sleep(0.1) 