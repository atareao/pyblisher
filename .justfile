user    := "atareao"
name    := `basename ${PWD}`
version := `git tag -l  | tail -n1`

build:
    echo {{version}}
    echo {{name}}
    podman build -t {{user}}/{{name}}:{{version}} \
                 -t {{user}}/{{name}}:latest \
                 .

push:
    podman push {{user}}/{{name}}:{{version}}
    podman push {{user}}/{{name}}:latest

build-test:
    echo {{version}}
    echo {{name}}
    podman build -t {{user}}/{{name}}:test \
                 .
run-test:
    podmn run --rm \
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
