FROM node:17-alpine

EXPOSE 80
COPY * /app/
WORKDIR /app



# Python config
RUN apk update || : && apk add python3 py3-pip npm
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh

#nodejs config
RUN npm install -g nodemon

# cron config
#RUN apk add cron
COPY cron-config /etc/cron.d/cron-config
RUN chmod 0644 /etc/cron.d/cron-config
RUN crontab /etc/cron.d/cron-config
RUN touch /var/log/eis-scraper.log
 
# Run the command on container startup
CMD ["node", "index.js"]
CMD /app/entrypoint.sh