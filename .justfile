user    := "atareao"
name    := `basename ${PWD}`
version := `git tag -l  | tail -n1`

default:
    @just --list

rebuild:
    echo {{version}}
    echo {{name}}
    docker build --no-cache \
                 -t {{user}}/{{name}}:{{version}} \
                 -t {{user}}/{{name}}:latest \
                 .
build:
    echo {{version}}
    echo {{name}}
    DOCKER_BUIDKIT=1 docker build \
                -t {{user}}/{{name}}:{{version}} \
                -t {{user}}/{{name}}:latest \
                .

push:
    docker push {{user}}/{{name}}:{{version}}
    docker push {{user}}/{{name}}:latest

build-test:
    echo {{version}}
    echo {{name}}
    docker build -t {{user}}/{{name}}:test \
                 .
test:
    docker run --rm \
               --init \
               --name {{name}} \
               --detach \
               -p 8000:8000 \
               --volume $PWD/threads.conf:/app/threads.conf \
               --volume $PWD/twitter.conf:/app/twitter.conf \
               --volume $PWD/database.db:/app/database.db \
               --volume $PWD/peertube.toml:/app/peertube.toml \
               --volume /etc/timezone:/etc/timezone:ro \
               --volume /etc/localtime:/etc/localtime:ro \
               --env-file .env \
               {{user}}/{{name}}:latest
stop:
    docker stop {{name}}

run:
    gunicorn main:app -k uvicorn.workers.UvicornWorker \
             -w 1 \
             --chdir src \
             --threads 1 \
             --access-logfile - \
             -b 0.0.0.0:8000
