import pyttsx3
import atexit
import json
import getpass
import platform, re, os, sys, time
import emoji
from fbchat import log, Client

#Set up the TTS engine (different voices available on macOS, in a different order)
engine = pyttsx3.init()
voices = engine.getProperty('voices')

#Get creds
username = input('Username: ') #Can leave these blank if logging in with cookies
password = getpass.getpass() 
langCode = input('Language (en_US*, zh_TW etc.): ') #For Windows, you must have the language installed
if(langCode=='') or (langCode=='en_US'):
    if platform.system()=='Darwin':
        engine.setProperty('rate', 120)
        maleVoice = voices[7]
        femaleVoice = voices[33]
    else:
        engine.setProperty('rate', 115)
        maleVoice = voices[0]
        femaleVoice = voices[1]
else:
    for x in voices:
        if (x.languages[0]==langCode):
            maleVoice = x
            femaleVoice = x
            break
        else:
            x = None  
    if (x==None):
        print('No appropriate voice found for', langCode)    
        quit()     

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

def demoji(text): 
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text

cookies = load_cookies(os.path.join(sys.path[0], 'session.json'))

#subclass for reader
class reader(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        #self.markAsRead(thread_id)

        #log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        
        #wait 2 seconds to check if message is still unread, if yes, then read it out
        time.sleep(2)
        if(readerClient.fetchThreadMessages(thread_id=thread_id, limit=1)[0].is_read==False):
            # If you're not the author, read out (nick)name (stripped of emojis) and message (or "sticker"/"attachment"), use gender appropriate voice
            if author_id != self.uid:
                user = readerClient.fetchUserInfo(author_id)
                
                if(user[author_id].nickname==None):
                    user[author_id].nickname = user[author_id].name
                elif (demoji(user[author_id].nickname).strip()==''):
                    user[author_id].nickname = user[author_id].name
                
                if(re.match('female*',user[author_id].gender)!=None):
                    engine.setProperty('voice', femaleVoice.id)
                else:
                    engine.setProperty('voice', maleVoice.id) 
                
                engine.say(demoji(user[author_id].nickname)) #cuz I'm super popular and have more than 1 friend who sends me messages, right?
                if(message_object.text!=None): #Too lazy to specify whether attachment or images
                    engine.say(message_object.text)
                elif(message_object.sticker!=None):
                    engine.say('Sticker')
                else:
                    engine.say('Attachment')
                engine.runAndWait()
                engine.stop()
            
#Initiate client
readerClient = reader(getpass.getuser(), password, session_cookies=cookies)

#Save session cookies to file when the program exits
atexit.register(lambda: save_cookies(os.path.join(sys.path[0], 'session.json'), readerClient.getSession()))

#Start client listening (goes after atexit)
readerClient.listen()
