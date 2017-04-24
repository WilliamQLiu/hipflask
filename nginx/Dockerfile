FROM ubuntu:latest
MAINTAINER Will Liu "william.q.liu@gmail.com"
RUN apt-get update -y
RUN apt-get install -y vim nginx
WORKDIR /etc/nginx
RUN rm -v /etc/nginx/sites-available/default
RUN rm -v /etc/nginx/sites-enabled/default
ADD confs/sites/hipflask /etc/nginx/sites-enabled/hipflask
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
