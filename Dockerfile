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

FROM alpine:3.17

ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

COPY --from=builder /opt /opt

RUN echo "**** install Python ****" && \
    apk add --update --no-cache \
            su-exec~=0.2 \
            ffmpeg~=5.1 \
            curl~=7.87 \
            python3~=3.10 && \
    mkdir -p /app/tmp && \
    mkdir -p /app/conf

COPY entrypoint.sh run.sh /
COPY ./src /app/

WORKDIR /app

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
CMD ["/bin/sh", "/run.sh"]
