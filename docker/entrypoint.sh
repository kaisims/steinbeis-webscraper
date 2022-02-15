printenv > /etc/environment

node index.js
cron && tail -f /var/log/eis-scraper.log