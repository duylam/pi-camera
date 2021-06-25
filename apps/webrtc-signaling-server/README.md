A web server app to forward WebRTC Signaling messages for clients

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
1. To start server app with hot-reloads: `npm run dev`

# 3. Other commands

1. To update TOC in README, run `npm run update-toc`.
1. To compile .proto to nodejs, run `npm run compile-proto`.
1. To install new library: `npm i -P <name>`.

