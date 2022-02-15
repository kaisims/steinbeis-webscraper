printenv > /etc/environment

echo "start node server"
nohup nodemon index.js </dev/null &
echo "start cronjob"
cron && tail -f /var/log/eis-scraper.log
