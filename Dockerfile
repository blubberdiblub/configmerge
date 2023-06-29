FROM alpine:3.16
LABEL maintainer=blubberdiblub@gmail.com
RUN apk add --no-cache python3
RUN python3 -m ensurepip --default-pip
RUN pip3 install --no-cache --upgrade pip setuptools wheel
COPY requirements.txt /root/requirements.txt
RUN pip3 install --no-cache -r /root/requirements.txt
COPY configmerge.py /usr/local/bin/configmerge
ENTRYPOINT ["/usr/bin/python3", "/usr/local/bin/configmerge"]
CMD ["--help"]
