# our base image
FROM python:2.7

RUN apt-get update
RUN apt-get -y install nodejs
RUN apt-get -y install npm
RUN npm install -g bower
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN echo '{ "allow_root": true }' > /root/.bowerrc

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /usr/src/app
RUN mkdir -p /root/logs/video-app/
RUN python manage.py bower install

# specify the port number the container should expose
EXPOSE 8000

CMD /bin/bash server-entrypoint.sh
