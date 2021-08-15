A web server app to forward WebRTC Signaling messages for clients

# Table of Contents

<!-- toc -->

- [1. Development setup](#1-development-setup)
- [2. Coding workflow](#2-coding-workflow)
- [3. Other commands](#3-other-commands)

<!-- tocstop -->

# 1. Development setup 

1. Install NodeJS v14
1. Consul necessary environment variables in `src/lib/config.js`
1. (Optional) Create `.env.local` file to set value for them in local (ignored by git). The content is like

```bash
PI_MEETING_REST_PORT=4001
PI_MEETING_HEARTBEAT_INTERVAL_MS=5000
```

# 2. Coding workflow

1. To install libraries: `npm i`
1. To start server app with hot-reloads: `npm start`

# 3. Other commands

1. To update TOC in README, run `npm run update-toc`.
1. To compile .proto to nodejs, run `npm run compile-proto`.
1. To install new library: `npm i -P <name>`.
1. To create docker image: `npm run dockerize`.
1. To turn on debug for gRPC, run `GRPC_VERBOSITY=DEBUG GRPC_TRACE=all npm start`. See [doc](https://github.com/grpc/grpc/blob/master/doc/environment_variables.md)

