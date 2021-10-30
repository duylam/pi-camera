Start 3rd-party services. Make sure to install [docker](https://docs.docker.com/engine/install/) before continuing

> Below commands are supposted to run where current working dir is at this folder

**To start in local machine**

`bash scripts/dev-start.sh`

- See `src/start.sh` for supported environments
- Listen ports:
  * gRPC 4001
  * UDP 3478

**If web-viewer and pi-client are in local machine, set PI_MEETING_ADVERTISED_IP=127.0.0.1**

**If web-viewer and pi-client are in local network, set PI_MEETING_ADVERTISED_IP=<local IP>**

**If deploying on Internet, leave PI_MEETING_ADVERTISED_IP empty**

**To create build package for running on server**

- Run `bash scripts/build.sh` which will produce `build` forder to run. The folder has `start.sh` to launch services, see that file for environment variables

**Other commands**

- Run STUN client and verify STUN server, execute `docker run --rm -ti coturn/coturn:4.5.2-alpine turnutils_stunclient -p <STUN server port> <STUN server hostname>`

