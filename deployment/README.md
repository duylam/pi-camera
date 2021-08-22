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

  - Install Docker Engine and Docker Compose

```bash
ssh pi-meeting-server 'bash -e -s' < ./install-docker.sh
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

# 3. Test deploy in local machine

We can test the deploy by using an Ubuntu virtual machine on local. Below are steps to go through above procedure with virtual Ubuntu machine

- Install [Vagrant](https://learn.hashicorp.com/tutorials/vagrant/getting-started-install?in=vagrant/getting-started)
- Open Terminal, navigate to `ubuntu-18` folder and execute `vagrant up`
- Execute deployment (above sections) on the Ubuntu virtual machine. Please note that the Ubuntu is already setup for docker automatically
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

