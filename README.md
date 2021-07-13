# Steinbeis EIS web-scraper
This python script scrapes the [EIS of the Steinbeis University](https://www.eis-scmt.com/) in order to look for new grades. Unfortunately the Steinbeis University doesn't informs the students about new grades, so I made this script and installed it on a vServer with cron running it every 5 minutes.

# Installation
Install python3 and pip
```bash
sudo apt-get install python3 pip
```
</br>

Install BeutifulSoup
```bash
pip install beautifulsoup4
```
</br>

Insert your credentials in `main.py` (line 14 - 17)
```python
eisCredentials = {
    'username': 'myemail@domain.de',
    'password': 'P4ssw0rD'
}
```

# 