import re

from KodiEasyShow.showScanner import ShowScanner
from KodiEasyShow.kodiController import KodiController   

#Initialize all shows on load
show_scanner = ShowScanner()
shows = show_scanner.get_shows()
WORDS = show_scanner.get_words()

kodi_controller = KodiController()

#TODO implement an algortihm for determinating the most matched from given words.
def most_matched(text):
    word_counter = {}
    for word in WORDS:
        #Skip words smaller then 4 chars
        if(len(word) < 4):
            continue

        if bool(re.search(r'\b%s\b'%(word), text, re.IGNORECASE)):
            matched_shows = show_scanner.match_shows(word)
            for show in matched_shows:
                if show in word_counter:
                    word_counter[show] += len(word)
                else:
                    word_counter[show] = len(word)
    print word_counter

    #Nothing found
    if len(word_counter) == 0:
        return None
    
    if len(matched_shows) > 1:
        max_counter = 0
        most_matched = None
        for show, counter in word_counter.items():
            if counter > max_counter:
                max_counter = counter
                most_matched = show
            elif counter == max_counter:
                #The string with least diff i.e. the shortest one matched
                most_matched = min([most_matched, show], key=len)

        return most_matched
    else:
        return matched_shows[0]
        

def handle(text, mic, profile):
    show = most_matched(text)
    
    if show:
        latest_episode = show_scanner.find_latest_episode(most_matched_show)
        if latest_episode:
            kodi_controller.play_file(latest_episode)
        else:
            mic.say("No episodes found")

    else:
        mic.say("Not found")

def isValid(text):
    search_shows = str.join("|", WORDS)
    return bool(re.search(r"\b(%s)\b"%(search_shows), text, re.IGNORECASE))

#Not run on import
def main():
    show_words = "family"
    #shows = show_scanner.match_shows(show_word)
    #episode = show_scanner.find_latest_episode(shows[0])
    show = most_matched(show_words)
    episode = show_scanner.find_latest_episode(show)
    print("found episode %s"%(episode))
    #kodi_controller.play_file(episode)

#Just for testing
if __name__ == "__main__":
    main()


