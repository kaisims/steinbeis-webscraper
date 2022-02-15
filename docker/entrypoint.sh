printenv > /etc/environment

echo "start node server"
nodemon index.js
echo "start cronjob"
cron && tail -f /var/log/eis-scraper.log
