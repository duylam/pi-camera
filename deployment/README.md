The document for how to deploy all apps in this repo to an Ubuntu server

# 1. Setup

1. Prepare a Ubuntu server
1. Allow access to remote Ubuntu server by appending below to `~/.ssh/config` in local machine. Feel free to use any name for `Host`, we will use `pi-camera-server` on this doc

```
Host pi-camera-server
  Hostname <IP>
  User <username>
  StrictHostKeyChecking no
  IdentityFile </path/to/private/ssh/key>
```

3. Setup docker for remote server, run below commands in local machine

  - Install Docker Engine and Docker Compose

```bash
ssh pi-camera-server 'bash -e -s' < ./install-docker.sh
```

  - Test docker

```bash
ssh pi-camera-server docker run --rm hello-world
```

4. Create folder for apps

```bash
ssh pi-camera-server 'mkdir -p ~/pi-camera/web-viewer ~/pi-camera/vendor ~/pi-camera/signaling'
```

5. Set environment variables for remote server, go to remote server, and append below content in `~/.profile`

```bash
server_id=<server public ip>
export PI_CAMERA_DOWNSTREAM_HOSTNAME_AND_PORT=$server_id:4001
export VUE_APP_WEBRTC_ICE_SERVER_URLS=stun:$server_id:3478?transport=udp
export VUE_APP_GRPC_API_BASE_URL=http://$PI_CAMERA_DOWNSTREAM_HOSTNAME_AND_PORT
```

6. Make sure the firewall setting (e.g. AWS EC2 Security Group) are
  - Allow anywhere incoming UDP from anywhere to the server
  - Allow outgoing UDP to anywhere from the server

# 2. Deploy

- On each app, create build package (see corresponding README for build command)
- Copy build package to corresponding folder at remote server, below is sample snippet, do the same for other 

```bash
cd apps/vendor-services

# Build it
# ..

# Copy package to remote server and extract it
tar -c build/ | ssh pi-camera-server 'cat >/tmp/vendor.tar'; ssh pi-camera-server 'tar -xf /tmp/vendor.tar -C ~/pi-camera/vendor/'
```

- Go to remote server at corresponding folder and launch app by `start.sh` file

# 3. Test deploy in local machine

We can test the deploy by using an Ubuntu virtual machine on local. Below are steps to go through above procedure with virtual Ubuntu machine

- Install [Vagrant](https://learn.hashicorp.com/tutorials/vagrant/getting-started-install?in=vagrant/getting-started)
- Open Terminal, navigate to `ubuntu-18` folder and execute `vagrant up`
- The Ubuntu virtual machine has:
  * Docker is installed automatically (with above script)
  * Inside the machine, the folder `/host_disk` is mapped to the root folder of this git repo
  * Ports are mapped to host machine
    - `guest: 3478, host: 3478, protocol: "udp"`
    - `guest: 4000, host: 4000, protocol: "tcp"`
  * The host machine can access the virtual machine by private IP, execute `vagrant ssh -c ifconfig` to see what is the IP
- Execute deployment (above sections) on the Ubuntu virtual machine
- Some basic vagrant commands
  * To access to virtual machine, execute `vagrant ssh`.
  * To stop the machine, execute `vagrant halt`.
  * To destroy the machine, execute `vagrant destroy`.
- See [Vagrant docs](https://www.vagrantup.com/docs) for further needs

**Troubleshooting**

- If executing `docker` raises below error, restart the virtual machine and try again

```
docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create": dial unix /var/run/docker.sock: connect: permission denied.
See 'docker run --help'.
```

