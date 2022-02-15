FROM node

EXPOSE 80
COPY * /app/
WORKDIR /app

#nodejs config
RUN npm install -g nodemon

# Python config
RUN apt-get update || : && apt-get install python3 python3-pip -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh

# cron config
RUN apt-get -y install cron
COPY cron-config /etc/cron.d/cron-config
RUN chmod 0644 /etc/cron.d/cron-config
RUN crontab /etc/cron.d/cron-config
RUN touch /var/log/eis-scraper.log
 
# Run the command on container startup
CMD ["node", "index.js"]
CMD /app/entrypoint.sh