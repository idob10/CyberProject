import requests
import os
import time
import simplejson
import httplib2
import json
from win32con import FALSE
FOLDER_PATH = "serverfiles"
FLAG_IN_USE = {'state':False}

key = '1654c202896c246e96c4f3d0180aa0879aede79c3eeaa067cd284771a2182049'

def checkkey(kee):
		if len(kee) == 64:
			return kee
		else:
			print ("There is something wrong with your key. Not 64 Alpha Numeric characters.")
			exit()
			
def checkhash(hsh):
		if len(hsh) == 32:
			return hsh
		elif len() == 40:
			return hsh
		elif len(hsh) == 64:
			return hsh
		else:
			print ("The Hash input does not appear valid.")
			exit()
			
def fileexists(filepath):
		if os.path.isfile(filepath):
			return filepath
		else:
			print ("There is no file at:" + filepath)
			exit()


# Request the file to VirusTotal.com
def send_file(filename):
    json = post_multipart("https://www.virustotal.com/api/scan_file.json", {'key':key}, filename)
    return simplejson.loads(json)


def handleChange(change):
	#Run for an input file + key
	a = send_file(change)
	res = VT_Request(key, a['resource'])
	while res==False:
		res = VT_Request(key, a['resource'])
	
	print(res.replace(a['resource'],change.split("\\",1)[1]))

# Perform an HTTP POST request
def post_multipart(url, fields, filepath):
    api_url = 'https://www.virustotal.com/vtapi/v2/file/scan' 
    params = dict(apikey=fields['key']) 
    with open(filepath, 'rb') as file:
        FLAG_IN_USE['state'] = True
        files = dict(file=(filepath, file)) 
        response = requests.post(api_url, files=files, params=params) 
        if response.status_code == 200: 
            result=response.json()
    file.close()
    FLAG_IN_USE['state'] = False
    return json.dumps(result, sort_keys=False, indent=4)


def VT_Request(key, hash):
    params = {'apikey': key, 'resource': hash}
    url = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
    while (url.status_code==204):
        url = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
    json_response = url.json()
    response = int(json_response.get('response_code'))
    if response == 0:
        return False

    elif response == 1:
        positives = int(json_response.get('positives'))
        if positives == 0:
            return f"{hash} is not malicious"
        else:
            return f"{hash} is malicious"
    else:
        return False