import urllib
import urllib2
import re
import json
import os
import rarfile


XBMC_ADDR = "192.168.1.6"
XBMC_PORT = "80"
JSONRPC_VER = "2.0"
TV_SHOW_PATH = "smb://FREENAS/data/Serier/"
TV_SHOW_MNT_PATH = "/mnt/data_nas/Serier/"
ACCEPTED_EXTENSIONS = ["mkv", "avi", "rar"]

WORDS = []
WORDS_MAPPING = {}

def is_playable(file_path):
    return (len(file_path) > 3 and file_path[-3:] in ACCEPTED_EXTENSIONS)

def get_latest_file(path):
    latest_time = 0
    latest_file = "NOT_FOUND"

    for item in os.listdir(path):
        file_path = path+"/"+item
        if os.path.isdir(file_path):
            file_path, created = get_latest_file(file_path) 
            if created > latest_time:
                latest_time = created
                latest_file = file_path
        else:
            if is_playable(file_path):
                created = os.path.getmtime(file_path)
                if created > latest_time:
                    latest_time = created
                    latest_file = file_path

    return (latest_file, latest_time)

def set_words(shows):
    for show in shows:
        for show_word in re.findall(r"[^ _\.]+", show):
            if show_word in WORDS_MAPPING.keys():
                WORDS_MAPPING[show_word].append(show)
            else:
                WORDS_MAPPING[show_word] = [show]
            WORDS.append(str.upper(show_word))

    print("words=%s"%(str(WORDS)))
    print("words_mapping=%s"%(str(WORDS_MAPPING)))

def get_all_shows():
    shows = []
    if(os.path.isdir(TV_SHOW_MNT_PATH)):
        for path in os.listdir(TV_SHOW_MNT_PATH):
            if(os.path.isdir(TV_SHOW_MNT_PATH+path)):
                shows.append(path)
    else:
        raise IOError("TV_SHOW_MNT_PATH:'%s' is not a directory"%(TV_SHOW_MNT_PATH))

    return shows

#Implement later
def file_is_rar(file_path):
    return (len(file_path) > 4 and file_path[-4:] == ".rar")

def rar_format(path, encoded_path):
    #Get the second last split, which usually is the filename without the extension
    #real_filename = path.split(urllib.quote_plus("/"))[-2] + ".mkv"
    rar_info = rarfile.RarFile(path).infolist()
    
    #If more files then one just take first file
    if len(rar_info) > 1:
        print("WARNING! Multiple files in rar, only supports one. First file is used")

    print rar_info[0].filename
    real_filename = rar_info[0].filename
    #real_filename = real_filename"
        
    return "rar://%s/%s"%(encoded_path, real_filename)

def create_json_rpc(method, params):
    json_data = {"jsonrpc":("%s")%(JSONRPC_VER),
                 "method" : method,
                 "params" : params,
                 "id" : 1}

    return json_data

def play_file(path):
    encoded_path = urllib.quote_plus(TV_SHOW_PATH + path)
    if file_is_rar(path):
        encoded_path = rar_format(path, encoded_path)
    
    print("encoded_path=%s"%(encoded_path))
    method = "Player.Open"
    params = {"item":{"file":encoded_path}}
    json_data = create_json_rpc(method, params)
    send_to_xbmc(json_data)

def send_to_xbmc(json_data):
    req = urllib2.Request("http://%s/jsonrpc"%(XBMC_ADDR))
    print json_data
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req, json.dumps(json_data))

def handle(text, mic, profile):
    found = False
    for word in WORDS:
        if bool(re.search(r'\b%s\b'%(word), text, re.IGNORECASE)):
            mic.say("playing family guy")
            main()
            found = True
            break

    if not found:
        mic.say("not found")

def isValid(text):
    return bool(re.search(r"\b(family|guy)\b", text, re.IGNORECASE))

def main():
    file_name = "Family Guy/S12/Family.Guy.S12E18.720p.HDTV.x264-REMARKABLE/family.guy.s12e18.720p.hdtv.x264-remarkable.rar"
    #play_file(file_name)
    shows = get_all_shows()
    set_words(shows)
    print("latest_file: %s"%(str(get_latest_file(TV_SHOW_MNT_PATH+shows[10]))))
    play_file(get_latest_file(TV_SHOW_MNT_PATH+shows[10])[0])
    print("done")

if __name__ == "__main__":
    main()
