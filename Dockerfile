ARG alpine_version=3.22.2
FROM alpine:${alpine_version}
RUN apk add --no-cache python3

ARG command="configmerge"
ARG rootdir="/opt/configmerge"
RUN ln -s -- "${rootdir}/bin/${command}" "/usr/local/bin/${command}"
ARG uid=1000
ARG user="$command"
RUN adduser -D -u ${uid} -- "${user}"
RUN chown -- "${user}:" /opt
RUN chmod -- g+ws /opt
USER ${uid}
WORKDIR "/home/${user}"
RUN python3 -m venv "${rootdir}"
RUN . "${rootdir}/bin/activate" && pip3 install --no-cache-dir --only-binary=:all: --no-compile --upgrade pip setuptools
ARG requirements
RUN . "${rootdir}/bin/activate" && pip3 install --no-cache-dir --only-binary=:all: --compile -- ${requirements}
COPY configmerge.py "${rootdir}/bin/${command}"
RUN sed -i -e "1s:^#!.*:#!${rootdir}/bin/python3 -I:" -- "${rootdir}/bin/${command}"
ENTRYPOINT ["/opt/configmerge/bin/python3", "-I", "/opt/configmerge/bin/configmerge"]
CMD ["--help"]

ARG maintainer="blubberdiblub@gmail.com"
LABEL org.opencontainers.image.authors="${maintainer}"
