# our base image
FROM python:2.7-onbuild

# specify the port number the container should expose
EXPOSE 8000

CMD /bin/bash server-entrypoint.sh
