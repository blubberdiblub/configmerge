ARG alpine_version=3.16.8
FROM alpine:${alpine_version}
RUN apk add --no-cache python3
RUN python3 -m ensurepip --default-pip
RUN pip3 install --no-compile --only-binary=:all: --no-cache-dir --upgrade pip setuptools
ARG requirements
RUN pip3 install --compile --only-binary=:all: --no-cache-dir -- ${requirements}
ARG uid=1000
ARG user=configmerge
RUN adduser -D -u ${uid} ${user}
COPY --chown=${uid}:${uid} --chmod=0555 configmerge.py /usr/local/bin/configmerge
WORKDIR /home/${user}
ENTRYPOINT ["/usr/bin/python3", "-I", "/usr/local/bin/configmerge"]
CMD ["--help"]
USER ${uid}
ARG maintainer=blubberdiblub@gmail.com
LABEL maintainer=${maintainer}
