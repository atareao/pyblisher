FROM alpine:3.17 as builder

LABEL maintainer="Lorenzo Carbonell <a.k.a. atareao> lorenzo.carbonell.cerezo@gmail.com"

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN echo "**** install Python ****" && \
    apk add --update --no-cache --virtual\
            .build-deps \
            gcc~=12.2 \
            musl-dev~=1.2 \
            python3-dev~=3.10 \
            python3~=3.10 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /
RUN echo "**** install Python dependencies **** " && \
    python3 -m venv ${VIRTUAL_ENV} && \
    ${VIRTUAL_ENV}/bin/pip install --upgrade pip && \
    ${VIRTUAL_ENV}/bin/pip install --no-cache-dir -r /requirements.txt

###

FROM alpine:3.17

ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1
ENV USER=app
ENV UID=10001

RUN echo "**** install Python ****" && \
    apk add --update --no-cache \
            ffmpeg~=5.1 \
            curl~=8.0 \
            python3~=3.10 && \
    mkdir -p /app/tmp && \
    mkdir -p /app/conf

COPY --from=builder /opt /opt
COPY entrypoint.sh run.sh /
COPY ./src /app/

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/${USER}" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    "${USER}" && \
    chown -R app:app /app


WORKDIR /app
USER app

CMD ["/bin/sh", "/run.sh"]
