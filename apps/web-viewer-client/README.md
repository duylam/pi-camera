A Web frontend app (VueJS) displays video from `pi-camera-client` in WebRTC protocol

# Table of Contents

<!-- toc -->

- [1. Development setup](#1-development-setup)
- [2. Coding workflow](#2-coding-workflow)
- [3. Other commands](#3-other-commands)

<!-- tocstop -->

# 1. Development setup 

1. Install NodeJS v14
1. (Optional) Necessary environment variables are declared in `.env` file with default value. For overriding them, copy it to `.env.local` and modify it (ignored by git)

# 2. Coding workflow

g. To install libraries: `npm i`
1. To start frontend app with hot-reloads: `npm start`

# 3. Other commands

1. To update TOC in README, run `npm run update-toc`.
1. To compile .proto to nodejs, run `npm run compile-proto`.
1. To install new node library: `npm i -D <name>`.
1. To build to frontend package

```bash
VUE_APP_GRPC_API_BASE_URL="http://localhost:4001" \
  VUE_APP_WEBRTC_ICE_SERVER_URLS="stun:localhost:3478?transport=udp" \ # optional
  npm run build
```

5. To run [Vue CLI](https://cli.vuejs.org/guide/): `npx vue-cli-service help`. Some common commands

  - To lint: `npx vue-cli-service lint`

# 3. Technical stack

- [WebRTC signaling workflow](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling)
- [CSS with Bulma framework](https://bulma.io/documentation/)
- [Icons with Font Awesome](https://fontawesome.com/v5.15/icons?d=gallery&p=2&m=free) ([<font-awesome-icon> reference](https://www.npmjs.com/package/@fortawesome/vue-fontawesome))

