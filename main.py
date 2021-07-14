import os 
import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup

session = requests.Session()
dir_path = os.path.dirname(os.path.realpath(__file__))

# Pushover Integration
# pushoverApiToken = 'apitokenformyapplication'
# pushoverClientId = 'givenclientid'

eisCredentials = {
    'username': sys.argv[1],
    'password': sys.argv[2]
}

postData = {
    'username': eisCredentials.get('username'),
    'password': eisCredentials.get('password'),
    'id': '20',
    'submitted': '1',
    'L': '',
    'type': '',
    'oitSource': 'login.html',
    'oitAction': 'doLogin',
    'Login': 'Login'
}

# get scmt cookies
res = session.get(url='https://www.eis-scmt.com/home/lib/Controller.php')

# make auth request to get session cookies
login = session.post(url= 'https://www.eis-scmt.com/home/lib/Controller.php', data=postData)

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

# look for older grades-data
try:
    oldgrades = []
    with open(dir_path + '/data.json') as json_file:
        oldgrades = json.load(json_file)
except FileNotFoundError:
    print(datetime.now(), "No data found on your device, generating new and restarting script...")
    with open(dir_path + '/data.json', 'w') as json_file:
        json.dump(grades, json_file,  indent=4)
    os.system("python3 init.py")
    exit()

# compare old with new grades
if oldgrades != grades:
    print(datetime.now(), 'Found new grades! Saving and notifying user.')
    updatedModules = [x for x in oldgrades + grades if x not in oldgrades]

    # write new grades data
    with open(dir_path + '/data.json', 'w') as json_file:
        json.dump(grades, json_file,  indent=4)

    # notify me with pushover
    # res = requests.post(url='https://api.pushover.net/1/messages.json', data={
    #     'token': pushoverApiToken,
    #     'user': pushoverClientId,
    #     'message': json.dumps(updatedModules),
    #     'title': 'New Grades!',
    #     'url': 'eis-scmt.com/',
    #     'url_title': 'Loginpage of the EIS'
    # })
else:
    print(datetime.now(), 'No new grades were discovered.')

exit()