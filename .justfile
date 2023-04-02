user    := "atareao"
name    := `basename ${PWD}`
version := `git tag -l  | tail -n1`

build:
    echo {{version}}
    echo {{name}}
    docker build -t {{user}}/{{name}}:{{version}} \
                 -t {{user}}/{{name}}:latest \
                 .

push:
    docker push {{user}}/{{name}} --all-tags

build-test:
    echo {{version}}
    echo {{name}}
    docker build -t {{user}}/{{name}}:test \
                 .
run-test:
    docker run --rm \
               --init \
               --name {{name}} \
               --detach \
               -p 8000:8000 \
               --volume $PWD/database.db:/app/database.db \
               --volume $PWD/peertube.toml:/app/peertube.toml \
               --volume /etc/timezone:/etc/timezone:ro \
               --volume /etc/localtime:/etc/localtime:ro \
               --env-file .env \
               {{user}}/{{name}}:test
