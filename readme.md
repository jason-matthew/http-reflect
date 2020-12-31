# Overview

Provide HTTPD image which reflects request details as the response body.

Image initially established to provide whats-my-ip functionality, expose HTTP client behaviors, and observe proxy modifications.

## Usage

Project scoped for use within private networks.  Project should not be exposed to public traffic.  

Functionality particularly helpful within large networks.  Service provides simple mechanism for docker containers to determine their host address.

### Setup

```bash
image=httpd-reflect:latest
container=reflect
exposed_port=80

# build image
docker build --rm -t "${image}" -f ./Dockerfile .

# start in background
docker run -d --rm --name ${container} -p ${exposed_port}:80 ${image}

# bring logs to foreground
docker logs -f ${container}
```

### Query

```bash
# across the network within a docker container
$ hostname -f
f18bd7bbc08b

$ hostname -i
172.17.0.2

$ curl -s reflect.example.org
{"ip": "10.1.2.3", "headers": {"host": "reflect.example.org", "accept": "*/*", "user-agent": "curl/7.29.0"}, "host": "build-node-01.example.org", "command": "GET", "context": "/", "query": {}, "path": "/", "data": null}

$ curl -s reflect.example.org?ip
10.1.2.3

$ curl -s reflect.example.org?host
build-node-01.example.org
```
