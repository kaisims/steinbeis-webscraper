printenv > /etc/environment

cron && tail -f /var/log/eis-scraper.log
#node /app/index.js