import os
import re

import config


class ShowScanner():
    _last_scan = 0;
    _show_list = []
    _word_mapping = {}

    _ACCEPTED_EXTENSIONS = ["mkv", "avi", "rar"]
    _SHOW_PATH = config.SHOW_MNT_PATH

    def __init__(self):
        self._update_shows()

    def _is_playable(self, file_path):
        return (len(file_path) > 3 and file_path[-3:] in self._ACCEPTED_EXTENSIONS)

    def _get_latest_file(self, path):
        latest_time = 0
        latest_file = None

        for item in os.listdir(path):
            file_path = path+"/"+item
            if os.path.isdir(file_path):
                file_path, created = self._get_latest_file(file_path) 
                if created > latest_time:
                    latest_time = created
                    latest_file = file_path
            else:
                if self._is_playable(file_path):
                    created = os.path.getmtime(file_path)
                    if created > latest_time:
                        latest_time = created
                        latest_file = file_path

        return (latest_file, latest_time)

    def _update_shows(self):
        """
        Check shows dir for shows and add them to _show_list
        """
        shows = []
        
        if(os.path.isdir(self._SHOW_PATH)):
            for path in os.listdir(self._SHOW_PATH):
                if(os.path.isdir(self._SHOW_PATH+path)):
                    shows.append(path)
        else:
            raise IOError("SHOW_PATH:'%s' is not a directory"%(self._SHOW_PATH))

        self._show_list = shows

    def get_words(self):
        """
        Gets all the different words used in all the shows 
        """
        words = []
        for show in self._show_list:
            for show_word in re.findall(r"[^ _\.]+", show):
                show_word = str.upper(show_word)
                if show_word in self._word_mapping.keys():
                    self._word_mapping[show_word].append(show)
                else:
                    self._word_mapping[show_word] = [show]
                
                #TODO - Check if word is in the list?
                words.append(show_word)

        return words

    def get_shows(self):        
        return self._show_list
        
    def match_shows(self, word):
        return self._word_mapping[word]

    def find_latest_episode(self, show):
        return self._get_latest_file(self._SHOW_PATH + show)[0]

    def _dir_changed(self):
        """
        Check if the dir has been changed since last scan
        """
        return True

    def update_thread(self):
        if self._dir_changed():
            pass
