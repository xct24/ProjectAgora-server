FROM python:3-alpine

RUN apt-get clean
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get update
RUN apt-get -f install -y nginx
ADD default /etc/nginx/sites-available
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 10081