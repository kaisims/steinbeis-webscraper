printenv > /etc/environment

echo "start node server"
node index.js
echo "start cronjob"
cron && tail -f /var/log/eis-scraper.log
