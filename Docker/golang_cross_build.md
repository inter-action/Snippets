
# GOLANG cross build on mac

details goes here [golang docker hub](https://hub.docker.com/_/golang/), include cross build for windows,

make sure your PWD is under your user path, like `docker run -v /Users/<path>:/<container path>`

    docker pull golang:1.3-onbuild

build go source file

    docker run --rm -v "$PWD":/usr/src/myapp -w /usr/src/myapp golang:1.3 go build -v

go development

    docker run --rm -it -v "$PWD":/usr/src/myapp -w /usr/src/myapp golang:1.3


you maybe need a docker file to install go dependencies first, like this,



    FROM golang:1.3.1-onbuild
    RUN go install github.com/go-sql-driver/mysql
    ...

    COPY . /go/src/app
    WORKDIR /go/src/app

    EXPOSE 80 443


    > docker build -t api .
    > docker run --name api-running -it --rm api

    1.build current directory into new docker image `api`
    2.run just builded image into a container named `api-running` in interactive mode, `--rm` remove previous container if existed


