# Steinbeis EIS web-scraper
This python script scrapes the [EIS of the Steinbeis University](https://www.eis-scmt.com/) in order to look for new grades and grade averages. Unfortunately the Steinbeis University doesn't inform the students about new grades or grade averages, so I made this script and installed it on a vServer with cron running it every 5 minutes.

# Installation
Install python3 and pip
```bash
> sudo apt-get install python3 pip
```
</br>

Install [BeutifulSoup](https://pypi.org/project/beautifulsoup4/)
```bash
> pip install beautifulsoup4
```
</br>

Now you can run the script with the following command
```bash
> python3 main.py <username> <password>
```
</br>

E.g. for the user `sandra.muster@domain.de` and her password `P4ssw0rD`

```bash
> python3 main.py sandra.muster@domain.de P4ssw0rD
```

# Setting up cron
To let cron run this script (e.g. on a vServer) you need to install the script on your machine like described before. After the installation you can follow the following steps

Execute crontab and edit the crontab config
```bash
> crontab -e
```
</br>

When never started crontab before: Choose nano as editor
```bash
> 1
```
</br>

After inserting the following line, save and exit it
```
*/5 * * * * /usr/bin/python3 /path/to/main.py <username> <password> >> /var/log/eis-scraper.log 2>&1
```
</br>

Next you have to restart the cron service to apply the changes you've made
```
> sudo systemctl restart cron
```
</br>

Now your cron-job is looking for new grades every 5 minutes. For a deeper dive into cron and crontab have a look at [this](https://www.adminschoice.com/crontab-quick-reference) tutorial.

# Notifications
I have implemented the notifications with the help of [Pushover](https://pushover.net/). The sample code is already in the script, just need to comment it out and enter your account credentials.

```python
pushoverApiToken = 'apitokenformyapplication'
pushoverClientId = 'givenclientid'
```