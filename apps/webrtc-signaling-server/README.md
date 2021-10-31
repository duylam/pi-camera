A web server app to forward WebRTC Signaling messages for clients

# Table of Contents

<!-- toc -->

- [1. Development setup](#1-development-setup)
- [2. Coding workflow](#2-coding-workflow)
- [3. Other commands](#3-other-commands)

<!-- tocstop -->

---

> Below commands are supposted to run where current working dir is at this folder

# 1. Development setup 

1. Install NodeJS v14

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash; nvm install 14.17.0
```

2. Consult necessary environment variables in `src/lib/config.js`
1. (Optional) Create `.env.local` file to set value for them in local (ignored by git). The content is like

```bash
PI_CAMERA_GRPC_PORT=4000
```

# 2. Coding workflow

1. To install libraries: `npm i`
1. To start server app with hot-reloads: `npm start`

# 3. Other commands

1. To update TOC in README, run `npm run update-toc`.
1. To compile .proto to nodejs, run `npm run compile-proto`.
1. To install new library: `npm i -P <name>`.
1. To build: `npm run build`.
1. To turn on debug for gRPC, run `GRPC_VERBOSITY=DEBUG GRPC_TRACE=all npm start`. See [doc](https://github.com/grpc/grpc/blob/master/doc/environment_variables.md)

