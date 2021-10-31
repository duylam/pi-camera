My pet project to setup video call room from 02 Pi devices. It's like [Google Meet Hardware](https://workspace.google.com/products/meet-hardware/) but much more simpler

# Applications

The software is made from several apps (listed in `/apps` dir):

- `pi-camera-client` app: a Python app runs on Raspberry Pi with Camera module
- `web-viewer-client` app: a VueJS web frontend app presents the camera in Raspberry Pi
- `webrtc-signaling-server` app: a NodeJs backend web app for handling WebRTC Signaling messages
- `vendor-services` is 3rd-party backend services

Consult README in `apps` folder for how to run them in local machine

# The repo structure

- `apps`: for apps
- `schema`: the shared schema for GRPC service and messages
- `deployment`: guideline and utils for deploying to your real environment

