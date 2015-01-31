import urllib
import urllib2
import json
import rarfile

import config

class KodiController():
    def _file_is_rar(self, file_path):
        return (len(file_path) > 4 and file_path[-4:] == ".rar")

    def _rar_format(self, path):
        #Get the second last split, which usually is the filename without the extension
        rar_info = rarfile.RarFile(path).infolist()
        
        #If more files then one just take first file
        if len(rar_info) > 1:
            print("WARNING! Multiple files in rar, "
                  "only supports one. First file is used")

        real_filename = rar_info[0].filename
        path = urllib.quote_plus(self._get_kodi_path(path))

        return "rar://%s/%s"%(path, real_filename)

    def _create_json_rpc(self, method, params):
        json_data = {"jsonrpc":("%s")%(config.JSONRPC_VER),
                     "method" : method,
                     "params" : params,
                     "id" : 1}
        return json_data

    def _get_kodi_path(self, path):
        """
        Replaces the mnt path to the kodi path
        """
        return config.SHOW_KODI_PATH + path[len(config.SHOW_MNT_PATH):]

    def play_file(self, path):    
        """
        Send a play request to kodi for given path
        """
    
        if self._file_is_rar(path):
            path = self._rar_format(path)
        else:
            path = self._get_kodi_path(path)

        method = "Player.Open"

        params = {"item":{"file":path}}
        json_data = self._create_json_rpc(method, params)
        self._send(json_data)

    def _send(self, json_data):
        print(json_data)
        req = urllib2.Request("http://%s/jsonrpc"%(config.KODI_ADDR))
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req, json.dumps(json_data))
        print(response.read())
