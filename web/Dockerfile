FROM python:3.5

RUN mkdir /web
WORKDIR /web

ADD requirements.txt /web/requirements.txt
ADD py_pkg /web/py_pkg

# By some unknown reason, pandas is requiring numpy to be installed not just being in the requirement.txt
# to install, so installing via requirement.txt is not possible
# pip install --download-cache="/pth/to/downloaded/files" package
#RUN pip install -r /web/requirements.txt
#RUN pip install --upgrade pip
#RUN pip install --no-index --find-links="/web/py_pkg" numpy
RUN pip install --no-index --find-links="/web/py_pkg" -r /web/requirements.txt