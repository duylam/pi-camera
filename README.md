A virtual meeting room software using Raspberry Pi. It provides standby video (from Pi Camera module) for remote people

# The software structure

The software is made from several components:

- `pi-camera-client` app: a Python app runs on Raspberry Pi with Camera module plugged 
- `web-viewer-client` app: a web frontend app that for users to see the camera in Raspberry Pi
- `webrtc-signaling-server` app: a backend web service for handling WebRTC Signaling messages
- `vendor-services` services: some 3rd-party backend services

Consult README files in `apps` folder for how to run each of them in local machine

# The repo structure

- `apps`: the folder for app components
- `schema`: the shared schema for GRPC service and messages
- `deployment`: utils for deploying to backend server

