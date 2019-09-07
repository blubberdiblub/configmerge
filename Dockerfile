FROM alpine:3.10
LABEL maintainer=blubberdiblub@gmail.com
RUN apk add --no-cache python3
RUN python3 -m ensurepip --default-pip
RUN pip3 install --no-cache --upgrade pip setuptools wheel
WORKDIR /opt/configmerge
COPY requirements.txt .
RUN pip3 install --no-cache -r requirements.txt
COPY configmerge.py bin/configmerge.py
ENTRYPOINT ["/usr/bin/python3", "/opt/configmerge/bin/configmerge.py"]
