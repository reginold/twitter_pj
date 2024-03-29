FROM mianasbat/ubuntu1804-py3.6-pip:latest
ENV PYTHONUNBUFFERED 1
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update && \
    apt-get -y install sudo


RUN sudo apt-get install tree

RUN DEBIAN_FRONTEND=noninteractivate apt-get install -y mysql-server
RUN sudo apt-get update
RUN sudo apt-get install -y libmysqlclient-dev gcc libmariadb-dev
RUN sudo apt-get install -y python3-pip
RUN sudo apt-get install -y python-setuptools redis

RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN pip3 install --upgrade setuptools
RUN pip3 install --ignore-installed wrapt
RUN pip3 install -U pip

COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

RUN mkdir /vagrant
WORKDIR /vagrant
COPY . /vagrant/

# RUN useradd -ms /bin/bash user
# RUN chown -R user: /vagrant
# USER user
# tempory detailing with making media folder
USER root



