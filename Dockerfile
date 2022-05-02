FROM alpine:3.15 as builder

ENV TZ=Europe/Madrid
LABEL maintainer="Lorenzo Carbonell <a.k.a. atareao> lorenzo.carbonell.cerezo@gmail.com"

ARG UID=${EB_UID:-1000}
ARG GID=${EB_GID:-1000}

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN echo "**** install Python ****" && \
    apk add --update --no-cache --virtual\
            .build-deps \
            gcc \
            musl-dev \
            python3-dev \
            python3==3.9.7-r4 && \
    rm -rf /var/lib/apt/lists/* && \
    echo "**** create user ****" && \
    addgroup dockerus && \
    adduser -h /app -G dockerus -D dockerus && \
    mkdir -p ${VIRTUAL_ENV} && \
    chown -R dockerus:dockerus ${VIRTUAL_ENV}

COPY requirements.txt /
USER dockerus
RUN echo "**** install Python dependencies **** " && \
    python3 -m venv ${VIRTUAL_ENV} && \
    ${VIRTUAL_ENV}/bin/pip install --upgrade pip && \
    ${VIRTUAL_ENV}/bin/pip install --no-cache-dir -r /requirements.txt

FROM alpine:3.15

ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

COPY --from=builder /opt /opt
COPY --from=builder /etc/group /etc/passwd /etc/shadow /etc/

RUN echo "**** install Python ****" && \
    apk add --update --no-cache \
            tini==0.19.0-r0 \
            tzdata==2022a-r0 \
            ffmpeg==4.4.1-r2 \
            python3==3.9.7-r4 && \
    mkdir -p /app/tmp && \
    mkdir -p /app/conf && \
    chown -R dockerus:dockerus /opt && \
    chown -R dockerus:dockerus /app

COPY entrypoint.sh /
USER dockerus

COPY --chown=dockerus:dockerus ./src /app/src/

WORKDIR /app

ENTRYPOINT ["tini", "--"]
CMD ["/bin/sh", "/entrypoint.sh"]
