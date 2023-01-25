# Lab: Load balancing with Nginx

**Load balancing** is an approach that allows to disribute incoming network
traffic across a group of backend servers efficiently. This group of backend
service is often called a server farm or a server pool.

Nginx is a web server that can also be used as a reverse proxy, load balancer,
mail proxy or HTTP cache. It is a [free](https://en.wikipedia.org/wiki/Free_software)
and [open-source software](https://en.wikipedia.org/wiki/Open-source_software),
released under the terms of the 2-clause [BSD license](https://en.wikipedia.org/wiki/BSD_licenses).
It is one of a few most popular software choises when in comes to load balancing
over HTTP.


## Goals of the lab

1. Learn how to install and run Nginx server on Ubuntu.
2. Learn how to create a server pool and to distribute incoming workload across it.
3. See how load balancing works hands-on.


## Pre-requisites

This repository contains a simple service written in Python. The service provides
a simple REST API over the HTTP protocol. The API consists of a single endpoint:

```
GET /colour
```

that returns a simple string with a colour, e.g., `BLUE`, `GREEN`, etc. The colour string is always returned in the upper case.

The service always listens to requests at port `80`.

The service reads the colour it returns from the environment variable called
`COLOUR`. It will fail to start, if the variable is not set. The value of this
variable is case insensitive.

The colour may be set to one of the following:

```
Red, Green, Blue, Orange, Pink, Fuchsia, Amber, Coral, Maroon
```

The service will fail to start, if the specified colour is not one from
the list above.


## [Task 1] Build a docker container image for the setice

Since the service is written in Python and requires some dependencies to be installed
it is better to package it into a container image. The service was tested with
Python 3.8. Instead of using Ubuntu as the base image you may use an official
image called `python` that already have both python and pip pre-installed.

Tags on that image correspond to the version of python installed in the image.
Images that are tagged with just a python version are based on Debian and are rather
heavy. Therefore it is recommended to use images tagged as "*-alpine" - those
are based on Alpine and are much smaller.

Do not forget to install the service's dependencies from the `requirements.txt`
file. Use `pip install -r requirements.txt` for that.


## [Task 2] Run a container from the created image

Run a container with `docker run` as usual. Do not forget to map port 80 to one of the ports
available on the server. Ports 8080-8090 and ports 80 and 443 are open. I do not
recommend to map container ports to the server's port 80 because it will conflict
with the following tasks.

Do not forget to configure the colour.


## [Task 3] Check that the service is working as intended

1. Use `docker logs` to check service logs. The `-f` switch allows to "follow"
the new logs. In case you use `-f` switch use `Ctrl+c` to exit the logs.
2. With your browser or with `curl` check whether you can get a colour string
from the service by sending the appropriate HTTP request. Please refer to
[Pre-requisites](#pre-requisites) for details.
3. Discuss what you observe.


## [Task 4] Simulate a failure

1. Use `docker stop` and `docker rm` to kill and remove the container - this
will simulate a failure of a service.
2. Check, if you can still get the colour the same way you did in the previous task.
3. Discuss what you observe.


## [Task 5] Run several other instances of the service

1. Run 3 or more containers with the service the same way you did in [Task 2](#task-2-run-a-container-from-the-created-image).
For now configure **different** colour for different service instance.
2. Do not forget to map port 80 of every container to a different port on the server.


## [Task 6] Check that created service instances work as intended

This task is similar to the [Task 3](#task-3-check-that-the-service-is-working-as-intended)
but you have to do it for every service instance.

1. Check, if service instances are running with `docker-logs`.
2. With your browser or with curl try getting a colour from different instances.
3. Discuss what you observe.


## [Task 7] Install Nginx

    Nginx listens on port 80 by default. To avoid errors, please stop and remove containers, whose ports were mapped to the port 80 of the server, if any.

    For the porpose of this lab all your personal user accounts were granted sudo permissions.

1. Install nginx to the server. The package name is `nginx`.
2. With your browser check that it works sending a GET request to `/` at port 80.
The response should show you a default nginx site.


## [Task 8] Configure Nginx as a load balancer for the service instances

Nginx stores its configuration is multiple files. The location of those files
may be different in different Linux distributions but they are normally located
somewhere under the `/etc` directory since it's the directory to store all
configuration files.

On Ubuntu nginx stores its main configuration file with some global settings at
`/etc/nginx/nginx.conf`. In our case we do not need to configure it. Please
explore this file and see what settings are configured there.

Individual sites are normally configured in individual configuration files. On
Ubuntu Nginx reads every text file from the `/etc/nginx/sites-enabled/` directory
and threats it as a configuration files.

Standard practice is to put individual configuration files for different sites
into `/etc/nginx/sites-available/` directory. This directory is not read by Nginx.
To enable a specific individual site you have to add a symlink for its configuration
file from `/etc/nginx/sites-available/` into `/etc/nginx/sites-enabled/`. If you
need to disable a site you delete an appropriate symlink from `/etc/nginx/sites-enabled/`.

This method allows to enable and disable individual sites while keeping their
configuration files safe.

1. Disable the `default` site by removing the appropriate symlink from
`/etc/nginx/sites-enabled/`.
2. Create a new configuration file in `/etc/nginx/sites-available/` for your site
with the following content:
```
upstream backend {
    
    # Adjust the following list to the list of the service instances.
    
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://backend;
    }
}
```
3. Enable your site by creating a symlink for the adding configuration file
into `/etc/nginx/sites-enabled/`.
4. Test the nginx configuration by running `nginx -t`
5. Since Nginx is running as a daemon (remember what it is?) you have to restart
it with the daemon management system, which in Ubuntu (as well as in many other Linux
distributions) is called `systemd`. The command line for restarting Nginx daemon is
```
systemctl restart nginx
```
6. Use `systemctl status nginx` to check the status of the Nginx daemon.

Your site should be available on the port `80` now.

## [Task 9] Try accessing the instances via the load balancer

1. With your browser or curl try to get colours several times from your service
by accessing it via the load balancer at port 80.
2. What do you observe? How are requests distrubuted?

    Note that browsers may cache responses so you will always get the same response.
    On Mac use cmd+shift+r to send the request and show the page without the cache. Alternatively use curl - it does not use cache.

## [Task 10] Examine the distribution of the requests

1. With the change of colours on different requests explore how default
Round Robin load balancing strategy works.
2. You may also use `docker logs` to confirm that requests are being
distributed.

Sometimes we may want to send more requests to certain instances, for instance when
they are running on more powerful hardware. Nginx supports specifying weights
for every backend instance. The bigger is the waight the more requests that instance
will get.

3. In the site's configuration file edit the weight of the instances by adding
`weight=N` parameter to every `server` directive inside the `upstream`:
```
upstream backend {
    
    # Adjust the following list to the list of the service instances.
    
    server 127.0.0.1:8081 weight=1;
    server 127.0.0.1:8082 weight=5;
}

..........

```
4. Test the configuration with `nginx -t` and restart the daemon, if the test
is successful.
5. Try getting colours several times.
6. Discuss what you observe.
7. Remove all `weight` parameters from Nginx configuration and restart the daemon.


## [Task 11] Run the instances with the same configuration

Now it's time to simulate a real-life situation. In production all instances of
a service normally have the same configuration and process queries the same way.

1. Stop and remove all running containers with the service.
2. Start 3 or more instances of the service with the same configuration.
3. Adjust nginx's configuration, if needed (if ports were changed).
4. Try running getting the colours and examine request distribution with
`docker logs`.

## [Task 12] Simulate a failure

1. Simulate a failure by stopping and removing one container.
2. Try getting the colours several times.
3. Did the failure affect your user experience like it did in [Task 4](#task-4-simulate-a-failure)?
4. You may play around by removing more containers.

## Cleaning up
1. Commit created nginx configurations to this repo into `nginx_config` folder.
2. Stop the server