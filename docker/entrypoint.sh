printenv > /etc/environment

cron && tail -f /var/log/eis-scraper.log
node index.js