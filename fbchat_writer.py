import pyttsx3
import atexit
import json
import getpass
from fbchat import Client
from fbchat.models import Message, ThreadType
import speech_recognition as sr
import os, re, sys, time

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

#Get creds
user = input('Username: ') #you can leave these blank if using cookies
password = getpass.getpass() 
langCode = input('Language (en-US*, zh-CN etc.): ')
if(langCode==''):
    langCode = 'en-US'

cookies = load_cookies(os.path.join(sys.path[0], 'session.json'))
       
#Initiate client
writerClient = Client(user, password, session_cookies=cookies)

#Save session cookies to file when the program exits
atexit.register(lambda: save_cookies(os.path.join(sys.path[0], 'session.json'), writerClient.getSession()))

run = True
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purpose, we're just using the default API key. Also I'm poor.            
        verbal_diarrhea = recognizer.recognize_google(audio, pfilter=0, language=langCode)
        if re.search('abracadabra', verbal_diarrhea):
            verbal_diarrhea = recognizer.recognize_google(audio, pfilter=0) #Do an en-US search instead cuz all my friends have English names.
            if(writerClient.searchForUsers(verbal_diarrhea.replace('abracadabra', ''))[0].is_friend==True):
                UID = writerClient.searchForUsers(verbal_diarrhea.replace('abracadabra', ''))[0].uid
                print('What to send to'+' '+writerClient.fetchUserInfo(UID)[UID].name)
                try: 
                    verbal_diarrhea = 'shazam' #Cancel keyword, set initially so it doesn't send "abracadabra ____"
                    verbal_diarrhea = r.recognize_google(r.listen(m))
                except:
                    pass
            else:
                verbal_diarrhea = 'shazam' #Cancel if you're about to send a message to a random account
                print("Not friends")

        else:
            UID = writerClient.fetchThreadList(limit=1)[0].uid
        if (re.search('shazam', verbal_diarrhea.lower())==None): #Cancel keyword
            print("To", writerClient.fetchUserInfo(UID)[UID].name+":", verbal_diarrhea)
            writerClient.send(Message(text=verbal_diarrhea), thread_id=UID, thread_type=ThreadType.USER)
        else: 
            print("Cancel initiated; nothing sent")
        
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))


r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background
stop_listening = r.listen_in_background(m, callback)

print("Listening...")
while (run==True): time.sleep(0.1) 