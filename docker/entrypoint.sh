printenv > /etc/environment

echo "start cronjob"
cron && tail -f /var/log/eis-scraper.log
echo "start node server"
node index.js