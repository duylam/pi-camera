The document for how to deploy all apps in this repo to an Ubuntu server

# 1. Setup

1. Prepare a Ubuntu server
1. Allow access to remote Ubuntu server by appending below to `~/.ssh/config` in local machine. Feel free to use any name for `Host`, we will use `pi-meeting-server` on this doc

```
Host pi-meeting-server
  Hostname <IP>
  User <username>
  StrictHostKeyChecking no
  IdentityFile </path/to/private/ssh/key>
```

3. Setup docker for remote server, run below commands in local machine

  - Install docker engine

```bash
curl https://get.docker.com/ | ssh pi-meeting-server 'bash -e -s' -
```

  - Install docker compose

```bash
ssh pi-meeting-server 'sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose; sudo chmod +x /usr/local/bin/docker-compose'
```

  - Run docker as non-root user

```bash
ssh pi-meeting-server 'sudo groupadd docker; sudo usermod -aG docker $USER'
```

  - Test docker

```bash
ssh pi-meeting-server docker run --rm hello-world
```

4. Create folder for apps

```bash
ssh pi-meeting-server 'mkdir ~/pi-meeting; mkdir ~/pi-meeting/web-viewer; mkdir ~/pi-meeting/vendor; mkdir ~/pi-meeting/signaling'
```

5. Set environment variables for remote server, go to remote server, and append below content in ~/.profile

```bash
export PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT="<EC2 public IP>:4001"
export PI_MEETING_UPSTREAM_HOSTNAME=signaling-app
export PI_MEETING_ADVERTISED_IP=<EC2 public IP>
```

# 2. Deploy

- On each app, create build package (see corresponding README for build command)
- Copy build package to corresponding folder at remote server, below is sample snippet, do the same for other 

```bash
cd apps/vendor-services

# Build it
# ..

# Copy package to remote server and extract it
tar -c build/ | ssh pi-meeting-server 'cat >/tmp/vendor.tar'; ssh pi-meeting-server 'tar -xf /tmp/vendor.tar -C ~/pi-meeting/vendor/'
```

- Go to remote server at corresponding folder and launch app by `start.sh` file

