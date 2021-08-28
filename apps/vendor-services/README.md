# 1. Setup

- Install [docker](https://docs.docker.com/engine/install/)

# 2. Workflows

## 2.1 Run local

`bash scripts/dev-start.sh`

- GRPC Web proxy listens on 4001 and proxies to 4000

## 2.2. Other commands

- Run STUN client and verify STUN server, execute `docker run --rm -ti coturn/coturn:4.5.2-alpine turnutils_stunclient -p <STUN server port> <STUN server hostname>`

## 2.3 Build

- Run `bash scripts/build.sh` which will produce `build` forder to run. The folder has `start.sh` to launch services, see that file for environment variables

