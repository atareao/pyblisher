###############################################################################
## Builder
###############################################################################
FROM alpine:3.20 AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN echo "**** install Python ****" && \
    apk add --update --no-cache --virtual \
            .build-deps \
            gcc~=13.2 \
            musl-dev~=1.2 \
            python3-dev~=3.12 \
            python3~=3.12 \
            py3-pip~=24.0 \
            pip install  --break-system-packages uv && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY pyproject.toml requirements.lock README.md ./

RUN echo "**** install Python dependencies ****" && \
    uv venv && \
    source .venv/bin/activate && \
    uv pip install --no-cache -r requirements.lock

###############################################################################
## Final image
###############################################################################
FROM alpine:3.20

LABEL maintainer="Lorenzo Carbonell <a.k.a. atareao> lorenzo.carbonell.cerezo@gmail.com"

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    USER=app \
    UID=10001

RUN echo "**** install Python ****" && \
    apk add --update --no-cache \
            ffmpeg~=6.1 \
            curl~=8.7 \
            python3~=3.12 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/tmp && \
    mkdir -p /app/conf && \
    mkdir -p /app/templates

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY run.sh ./src /app/
COPY ./templates /app/templates/

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

CMD ["/bin/sh", "/app/run.sh"]
