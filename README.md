0. OS Logistics:
================
0.1 Development environment: 
Description:	Ubuntu 22.04.2 LTS
Release:	22.04
Codename:	jammy
kernel: 5.19.0-46-generic

0.2 Integral Python version: 3.10.6

0.3 sudo permissions is needed for some of the actions.

1. Installing Docker on development machine:
============================================
1.1 Docker version:
1.1.1 Client: Docker Engine - Community
 Version:           26.0.0
 API version:       1.45
 OS/Arch:           linux/amd64
 Context:           rootless

1.1.2 Server: Docker Engine - Community
 Engine:
  Version:          26.0.0
  API version:      1.45 (minimum version 1.24)


2. Development wise host logistics:
==================================
2.1 Installed python3 venv
$ sudo apt install python3.10-venv


2.2 Installed curl (for testing purposes)
$ sudo apt install curl


3. Install and run the application:
===================================
3.1 Clone the repo from GitHub

3.2 cd to the project's root folder: openSourceIntServer (might be also opensourceintserver)
(from now and on assuming we are in the openSourceIntServer folder)

3.3 Make sure no services on the system listens on port 80:
$ sudo lsof -i :80

--> if this command has any output indicating on a process that listens to port 80/TCP --> terminate it

3.4 Setting "port mapping" to the docker instance so that the server will be able to listen on port 80/TCP:
3.4.1 Check the value of the net.ipv4.ip_unprivileged_port_start kernel parameter
$ sudo sysctl -a | grep net.ipv4.ip_unprivileged_port_start

--> if it is 80 or less (default, i.e. - if you did not explictly altered it, SHOULD be 1024), no need to perfrom the next step: 
3.4.2 Set this variable to 80 as follows:
$ sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80

3.4.3 Build the Docker image:
$ docker build -t open_src_container .

3.4.4 Run the Docker container:
$ docker run -p 127.0.0.1:80:8080/tcp open_src_container

NOTE: If you wish that the "inner" mapped of the server in the container will be different than the given in the example above,
you need to change it in the configuration file of the application (see later sections) AND to change the command respectively.


4. Install for development:
===========================
4.1 Follow steps 3.1 and 3.2 as above

4.2 Create a virtual environment for the project to run in:
$ python3 -m venv openSourceQueryProjectSrc_env

4.3 Source the venv:
$ source openSourceQueryProjectSrc_env/bin/actiavate

4.4 Install the project for development purposes:
$ python3 setup.py develop

4.5 In case you are using some IDE (PyCharm for instance), set the interpreter to the one from the above virtual 
env (i.e. - /full/path/to/openSourceIntServer/openSourceQueryProjectSrc_env/bin/python)


5. Application settings (configuration):
========================================
5.1 Under the root folder of the project there is the configuration file of the server named: openSourceIntSystemConfigurationFile.json

5.2 Caching tunning:
In order to minimze the amount of queries that the server sends towards remote open source servers, it implementes a chaching mechanism.
5.2.1 The maxNumOfItemsInCache controls how many entries will be kept in the cache (defaults to 100).
5.2.2 The maxDurationOfItemInCacheSeconds controls the amount of time after it, if queried, an entry is removed (defaults to 3600 seconds)


5.3 Open source servers:
The server is capable of query IP addresses from different servers. If you wish to add one, add an entry under the "servers" section 
by indicating the protocol (http - for HTTP and https - for HTTPS).
Also, the full URL used is needed under the "url" section.

5.4 Listening port:
Under the "localHttpServerInfo" section there is the port variable. Change it if you wish that the server will listen on a different port.
As for the comment in section 3.4.4, if you do change it, then in order to run it in a Docker container, do the following (assuming you change it 
to listen on port 8081):
$ docker run -p 127.0.0.1:80:8081/tcp open_src_container
