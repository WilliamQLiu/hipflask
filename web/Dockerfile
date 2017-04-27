FROM ubuntu:latest
MAINTAINER Will Liu "william.q.liu@gmail.com"
RUN apt-get update -y
RUN apt-get install -y vim python-pip python-dev build-essential
COPY ./requirements.txt /web/requirements.txt
WORKDIR /web
RUN pip install -r requirements.txt
COPY . /web
EXPOSE 5000
#RUN /usr/bin/python /web/scripts/create_db.py
#ENTRYPOINT ["python"]
#CMD ["hipflask.py"]
#CMD /usr/local/bin/uwsgi --ini uwsgi.ini