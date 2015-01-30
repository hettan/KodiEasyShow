import urllib
import urllib2
import re
import json
import os
import rarfile


XBMC_ADDR = "192.168.1.6"
XBMC_PORT = "80"
JSONRPC_VER = "2.0"
TV_SHOW_XBMC_PATH = "smb://FREENAS/data/Serier/"
TV_SHOW_MNT_PATH = "/mnt/data_nas/Serier/"
ACCEPTED_EXTENSIONS = ["mkv", "avi", "rar"]

WORDS = []
WORDS_MAPPING = {}

#TODO, thread to update the shows

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
            show_word = str.upper(show_word)
            if show_word in WORDS_MAPPING.keys():
                WORDS_MAPPING[show_word].append(show)
            else:
                WORDS_MAPPING[show_word] = [show]
            WORDS.append(show_word)

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

def file_is_rar(file_path):
    return (len(file_path) > 4 and file_path[-4:] == ".rar")

def rar_format(path, encoded_path):
    #Get the second last split, which usually is the filename without the extension
    rar_info = rarfile.RarFile(path).infolist()
    
    #If more files then one just take first file
    if len(rar_info) > 1:
        print("WARNING! Multiple files in rar, only supports one. First file is used")

    real_filename = rar_info[0].filename
        
    return "rar://%s/%s"%(encoded_path, real_filename)

def create_json_rpc(method, params):
    json_data = {"jsonrpc":("%s")%(JSONRPC_VER),
                 "method" : method,
                 "params" : params,
                 "id" : 1}

    return json_data


def get_xbmc_path(path):
    """
    Replaces the mnt path to the xbmc path
    """
    return TV_SHOW_XBMC_PATH + path[len(TV_SHOW_MNT_PATH):]

def play_file(path):    
    encoded_path = urllib.quote_plus(get_xbmc_path(path))
    if file_is_rar(path):
        encoded_path = rar_format(path, encoded_path)
    
    method = "Player.Open"
    params = {"item":{"file":encoded_path}}
    json_data = create_json_rpc(method, params)
    send_to_xbmc(json_data)

def send_to_xbmc(json_data):
    req = urllib2.Request("http://%s/jsonrpc"%(XBMC_ADDR))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req, json.dumps(json_data))

def handle(text, mic, profile):
    found = False
    for word in WORDS:
        if bool(re.search(r'\b%s\b'%(word), text, re.IGNORECASE)):
            tv_show = WORDS_MAPPING[word][0]
            mic.say("playing %s"%(tv_show))
            play_file(get_latest_file(TV_SHOW_MNT_PATH+tv_show)[0])
            found = True
            break

    if not found:
        mic.say("not found")

def isValid(text):
    search_shows = str.join("|", WORDS)
    return bool(re.search(r"\b(%s)\b"%(search_shows), text, re.IGNORECASE))

def main():
    play_file(get_latest_file(TV_SHOW_MNT_PATH+WORDS_MAPPING["FAMILY"][0])[0])
    print("done")

#Run on load
shows = get_all_shows()
set_words(shows)

if __name__ == "__main__":
    main()

