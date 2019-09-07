FROM python:3.7-alpine
LABEL maintainer=blubberdiblub@gmail.com
WORKDIR /opt/configmerge
COPY requirements.txt .
RUN pip install -r requirements.txt && rm -rf ~/.cache
COPY configmerge.py bin/configmerge.py
ENTRYPOINT ["python", "bin/configmerge.py"]
