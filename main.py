import os 
import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup

# Pushover Integration
PUSHOVER_API_TOKEN = 'apitokenformyapplication'
PUSHOVER_CLIENT_ID = 'givenclientid'

EIS_CREDENTIALS = {
    'username': sys.argv[1],
    'password': sys.argv[2]
}

POST_DATA = {
    'username': EIS_CREDENTIALS.get('username'),
    'password': EIS_CREDENTIALS.get('password'),
    'id': '20',
    'submitted': '1',
    'L': '',
    'type': '',
    'oitSource': 'login.html',
    'oitAction': 'doLogin',
    'Login': 'Login'
}

session = requests.Session()
dir_path = os.path.dirname(os.path.realpath(__file__))

# Scrapes the EIS to get current grades data
def getCurrentGrades():
    # get scmt cookies
    res = session.get(url='https://www.eis-scmt.com/home/lib/Controller.php')

    # make auth request to get session cookies
    login = session.post(url= 'https://www.eis-scmt.com/home/lib/Controller.php', data=POST_DATA)

    # check if login was successful
    if "Login fehlgeschlagen! Benutzername oder Passwort ist falsch." in login.text:
        print(datetime.now(), "Your username or password are wrong")
        exit()
    elif "Bitte aktivieren Sie Cookies" in login.text:
        print(datetime.now(), "Cookies aren't activated")
        exit()
    else:
        print(datetime.now(), "Logged in successfully")

    # get html of grades-view and parse it into beautiful-soup
    grades = session.get(url='https://www.eis-scmt.com/home/lib/Controller.php?oitSource=fm1004_studium.html&oitAction=noten_show').content
    soup_grades = BeautifulSoup(grades, 'html.parser')

    # extract modules and grades into a list of dicts
    grades = [{ modul.select_one('td:nth-of-type(1)').get_text() + ', ' + modul.select_one('td:nth-of-type(2)').get_text(): modul.select_one('td:nth-of-type(4)').get_text()} 
    for modul in soup_grades.select('tr[oitct="ctDataSetNext"]')]

    return grades

# Looks for previously generated data and loads it. 
# If no data is available the current grades are saved and
# the script will restart
def getSavedGrades():
    try:
        oldgrades = []
        with open(dir_path + '/data.json') as json_file:
            oldgrades = json.load(json_file)
            return oldgrades

    except FileNotFoundError:
        print(datetime.now(), "No data found on your device, generating new and restarting script...")

        grades = getCurrentGrades()
        with open(dir_path + '/data.json', 'w') as json_file:
            json.dump(grades, json_file,  indent=4)

        os.system("python3 main.py")
        exit()

# Notifyies a user via pushover
def notifyUser(updatedModules):
    # notify me with pushover
    res = requests.post(url='https://api.pushover.net/1/messages.json', data={
        'token': PUSHOVER_API_TOKEN,
        'user': PUSHOVER_CLIENT_ID,
        'message': json.dumps(updatedModules),
        'title': 'New Grades!',
        'url': 'eis-scmt.com/',
        'url_title': 'Loginpage of the EIS'
    })

def main(): 
    # get current grades
    grades = getCurrentGrades()

    # look for older grades-data
    oldgrades = getSavedGrades()

    # compare old with new grades
    if oldgrades != grades:
        print(datetime.now(), 'Found new grades! Saving and notifying user.')
        updatedModules = [x for x in oldgrades + grades if x not in oldgrades]

        # write new grades data
        with open(dir_path + '/data.json', 'w') as json_file:
            json.dump(grades, json_file,  indent=4)

        # Notify user via pushover
        #notifyUser(updatedModules)
    else:
        print(datetime.now(), 'No new grades were discovered.')

    exit()
 
if __name__ == "__main__": 
	main() 
