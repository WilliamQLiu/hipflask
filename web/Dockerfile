FROM ubuntu:latest
MAINTAINER Will Liu "william.q.liu@gmail.com"
RUN apt-get update -y
RUN apt-get install -y vim python-pip python-dev build-essential
ADD ./requirements.txt /web/requirements.txt
WORKDIR /web
RUN pip install -r requirements.txt
ADD . /web
#EXPOSE 5000
#ENTRYPOINT ["python"]
#CMD ["hipflask.py"]
#CMD /usr/local/bin/uwsgi --ini uwsgi.ini