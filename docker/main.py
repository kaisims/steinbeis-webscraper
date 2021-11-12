import os 
import requests
import json
import sys
from datetime import datetime, date
from bs4 import BeautifulSoup

# Pushover Integration
PUSHOVER_API_TOKEN = 'myPrivateToken'
PUSHOVER_CLIENT_ID = 'myPrivateClientID'

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
    session.get(url='https://www.eis-scmt.com/home/lib/Controller.php')

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
    grades = [{ 
        'moduleName': modul.select_one('td:nth-of-type(1)').get_text(),
        'grade': modul.select_one('td:nth-of-type(4)').get_text(), 
        'type': modul.select_one('td:nth-of-type(2)').get_text(),
        'date': modul.select_one('td:nth-of-type(7)').get_text(),
        'firstExaminer': modul.select_one('td:nth-of-type(8)').get_text(),
        'secondExaminer': modul.select_one('td:nth-of-type(9)').get_text(),
        'gradeAvg': ''
    } for modul in soup_grades.select('tr[oitct="ctDataSetNext"]')]

    # get averages for all modules
    gradeAvgs = []
    examGrades = [grade for grade in grades if grade.get("type") == "K"]

    # search for grade-averages for each module of type "K"
    for grade in examGrades:
        gradeAvg = getCurrentGradePointAverage(grade.get("moduleName"), datetime.strptime(grade.get("date"),'%Y-%m-%d').date() if grade.get("date") != "" else "")

        if gradeAvg != None and ("-" not in gradeAvg.get("avgGrade") or "ausstehend" not in gradeAvg.get("avgGrade")):
            gradeAvgs.append(gradeAvg)
    
    # add grade-averages to overall data collection
    for idx, grade in enumerate(grades):
        for gradeAvg in gradeAvgs:
            if grade.get("type") == "K" and grade.get("moduleName") == gradeAvg.get("module"):
                grades[idx]["gradeAvg"] = gradeAvg.get("avgGrade")

    return grades

# Looks for previously generated data and loads it. 
# If no data is available the current grades are saved and
# the script will restart
def getSavedGrades():
    try:
        oldgrades = []
        with open(dir_path + '/data.json') as json_file:
            oldgrades = json.load(json_file)
            json_file.close()
            return oldgrades

    except FileNotFoundError:
        print(datetime.now(), "No data found on your device, generating new and restarting script...")

        grades = getCurrentGrades()
        with open(f'{dir_path}/data.json', 'w') as json_file:
            json.dump(grades, json_file,  indent=4)
            json_file.close()

        os.system(f"python3 {dir_path}/main.py {sys.argv[1]} {sys.argv[2]}")
        exit()

# Notifyies a user via pushover
def notifyUser(updatedModules):
    # notify me with pushover
    for module in updatedModules:
        requests.post(url='https://api.pushover.net/1/messages.json', data={
            'token': PUSHOVER_API_TOKEN,
            'user': PUSHOVER_CLIENT_ID,
            'message': buildMessage(module),
            'title': f'Update in {module.get("moduleName")}',
            'url': 'eis-scmt.com/',
            'url_title': 'EIS login'
        })

def buildMessage(module):
    messageString = ''

    for idx, key in enumerate(module):
        if idx > 0: messageString += '\n'
        messageString += f'{key}: {module.get(key)}'

    return messageString

# Scrapes the grade-average page for a specific module
# Returns a dict of found data if the searched data is available
# If no data is found, "None" will be returned
def getCurrentGradePointAverage(moduleTitle, dateOfExam: date):
    if dateOfExam == "": return None

    reqUrl = f"https://www.eis-scmt.com/leitfaden/news/{dateOfExam.strftime('%m')}_{dateOfExam.strftime('%Y')}.html"
    
    res = requests.get(url=reqUrl)
    if not res.ok: return None

    soup_gradesAvgs = BeautifulSoup(res.content, 'html.parser')

    for modul in soup_gradesAvgs.select('tr'):
        if moduleTitle in modul.select_one('td:nth-of-type(3)').get_text() and dateOfExam.strftime('%d.%m.%Y') in modul.select_one('td:nth-of-type(1)').get_text():
            return {
                'module': moduleTitle, 
                'date': dateOfExam, 
                'avgGrade': modul.select_one('td:nth-of-type(4)').get_text().replace('\n', '')
            }
    
    return None

# Because grade averages will be deleted after a few weeks,
# it is necessary to check each relevant attribute to prevent data loss
# instead of just replacing a new dict if it differs from the old one
def getUpdatedModule(oldGrade, newGrade):
    returnGrade = oldGrade
    discvDiff = False

    if (oldGrade.get("grade") != newGrade.get("grade") and oldGrade.get("grade") == ""):
        returnGrade["grade"] = newGrade.get("grade")
        discvDiff = True

    if (oldGrade.get("date") != newGrade.get("date") and oldGrade.get("date") == ""):
        returnGrade["date"] = newGrade.get("date")
        discvDiff = True

    if (oldGrade.get("firstExaminer") != newGrade.get("firstExaminer") and oldGrade.get("firstExaminer") == ""):
        returnGrade["firstExaminer"] = newGrade.get("firstExaminer")
        discvDiff = True

    if (oldGrade.get("secondExaminer") != newGrade.get("secondExaminer") and oldGrade.get("secondExaminer") == ""):
        returnGrade["secondExaminer"] = newGrade.get("secondExaminer")
        discvDiff = True

    if (oldGrade.get("secondExaminer") != newGrade.get("secondExaminer") and oldGrade.get("secondExaminer") == ""):
        returnGrade["secondExaminer"] = newGrade.get("secondExaminer")
        discvDiff = True

    if (oldGrade.get("gradeAvg") != newGrade.get("gradeAvg") and oldGrade.get("gradeAvg") == ""):
        returnGrade["gradeAvg"] = newGrade.get("gradeAvg")
        discvDiff = True

    return discvDiff, returnGrade

def main(): 
    # get current grades
    grades = getCurrentGrades()

    # look for older grades-data
    oldgrades = getSavedGrades()

    # compare old with new grades
    if oldgrades != grades:
        modulesWithDiffs = [oldAndNew for oldAndNew in oldgrades + grades if oldAndNew not in oldgrades]
        changedModules = []

        # update old dataset to prevent data-loss
        for idx, oldgrade in enumerate(oldgrades):
            for updatedModule in modulesWithDiffs:

                # check if old and new data is relating to same module and exam-type
                if oldgrade.get("moduleName") == updatedModule.get("moduleName") and oldgrade.get("type") == updatedModule.get("type"):
                    result = getUpdatedModule(oldgrade, updatedModule)

                    # check if a change was detected
                    if result[0]:
                        changedModules.append(result[1])
                        oldgrades[idx] = result[1]

        # if changedModules is empty no changes were discovered
        if len(changedModules) > 0:
            print(datetime.now(), 'Updates discovered, saving and notifying user.')
            # write new grades data
            with open(dir_path + '/data.json', 'w') as json_file:
                json.dump(oldgrades, json_file, indent=4)
                json_file.close()
            
            # Notify user via pushover
            # notifyUser(changedModules)

        else:
          print(datetime.now(), 'No new grades were discovered.')

    else:
        print(datetime.now(), 'No new grades were discovered.')

    exit()
 
if __name__ == "__main__": 
	main() 
