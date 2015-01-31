import re

from KodiEasyShow.showScanner import ShowScanner
from KodiEasyShow.kodiController import KodiController   

#Initialize all shows on load
show_scanner = ShowScanner()
shows = show_scanner.get_shows()
WORDS = show_scanner.get_words()

kodi_controller = KodiController()

def handle(text, mic, profile):
    found = False
    word_counter = {}
    for word in WORDS:
        if bool(re.search(r'\b%s\b'%(word), text, re.IGNORECASE)):
            matched_shows = show_scanner.match_shows(word)
            for show in matched_shows:
                if show in word_counter:
                    word_counter[show] += len(word)
                else:
                    word_counter[show] = len(word)
   
    if len(word_counter) == 0:
        mic.say("Not found")
    else:
        most_matched_show = max(word_counter, key=word_counter.get)
        mic.say("Playing %s"%(most_matched_show))

        latest_episode = show_scanner.find_latest_episode(most_matched_show)
        if latest_episode:
            kodi_controller.play_file(latest_episode)
        else:
            mic.say("No episodes found")

def isValid(text):
    search_shows = str.join("|", WORDS)
    return bool(re.search(r"\b(%s)\b"%(search_shows), text, re.IGNORECASE))

#Not run on import
def main():
    show_word = "FAMILY"
    shows = show_scanner.match_shows(show_word)
    episode = show_scanner.find_latest_episode(shows[0])
    kodi_controller.play_file(episode)

#Just for testing
if __name__ == "__main__":
    main()

