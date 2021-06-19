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

1. To install libraries: `npm ci`
1. To start frontend app with hot-reloads: `npx vue-cli-service serve`

# 3. Other commands

1. To update TOC in README, run `npm run update-toc`.
1. To install new library: `npm i -D <name>`.
1. To build to frontend package: `npm run build`.
1. To run [Vue CLI](https://cli.vuejs.org/guide/): `npx vue-cli-service help`. Some common commands

  - To lint: `npx vue-cli-service lint`
