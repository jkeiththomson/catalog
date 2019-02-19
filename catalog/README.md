 Linux Server Configuration

## Table of Contents

- [Description](#description)
- [Addresses](#addresses)
- [Software Installed](#software-installed)
- [Configuration Changes](#configuration-changes)
- [Third Party Resources](#third-party-resources)

## Description

This is my solution to the "Configure Linux Server" project from Udacity's "Full Stack Web Developer" nanodegree course.

This README.md file contains the information required by the project rubic.

For those who need more detail, the file STEPS.md describes the step-by-step instructions that I followed to implement the solution.

## Addresses

URL: http://incredibleduc.com
IP Address: 18.237.175.26
SSH Port: 2200

## Software Installed

Operating System
- ubuntu v16.04
- finger

Firewall
- ufw v0.35 (came with Ubuntu instance)

Apache
- apache2 v2.4.18
- libapache2-mod-wsgi

Python
- python v2.7.12
- python-dev
- pip v8.1.1
- httplib2 v0.9.1
- requests v2.9.1

SQL Alchemy
- sqlalchemy v1.0.11
- sqlachemy_utils v0.33.11

Flask
- flask v0.10.1

Git
- git v.2.7.4

PostgreSQL
- postgresql v9.5.14
- psycopg2 v2.7.7

OAuth2 Client
- oauth2client 4.1.3


## Configuration Changes

Note: this is a high-level description of the changes I made to the Ubuntu server. For the exact step-by-step instructions, see STEPS.md.

### 1. Create SSH key pairs for two Ubuntu users
- Used `ssh-keygen` to create public and private keys for users "ubuntu" and "grader"

### 2. Create an instance of Ubuntu on an AWS server
- Created an instance named "Ubuntu-512MB-Oregon-1" which was assigned the IP address 18.237.175.26
- Uploaded the public key for user "ubuntu" to the server as part of instance creation process
- Updated the software that came pre-installed in the instance
- Set time zone to UTC

### 3. Set up SSH login for users "ubuntu" and "grader"
- Copied the private keys created in step 1 to `~/.ssh` on my Macbook
- chmod 600 on private keys
- Added the user "grader" to instance and gave it sudo privileges (password=fullstack)
- Copied grader's public key into `~/ssh/authorized_keys`

### 4. Set up ports and firewall for Ubuntu
- Disabled all ports for incoming requests
- Enabled port 2200 for ssh, 80 for www, 123 for ntp

### 5. Set up some security precautions in Ubuntu
- Prevent users from logging in with passwords
- Prevent users from logging in as `root`
- These are both controlled by flags in `/etc/ssh/sshd_config` and are already set to the proper values

### 6. Install all the software we will need
- Installed software modules are listed in the previous section

### 7. Get and deploy web app code
- Clone catalog project from Github
- Set up VirtualHost configuration for wsgi app in `/etc/apache2/sites-available/catalog.conf`
- Update catalog app to use PostgreSQL instead of SQL_Lite
- Set up database users: superuser "ubuntu" and restricted user "catalog"
- Initialize the database with its default catalog items

### 8. Enable the new web app
- Disabled the default app
- Enabled the catalog app

### 9. Add Google+ log in to web app
- Remove hard coded IP addresses, replace with domain name
- Change address records with web registrar Hover so domain name points to proper IP address
- Change config files on Ubuntu server to use domain name instead of IP address
  - `/etc/apache2/apache2.conf`
  - `/etc/apache2/sites-available/catalog.conf`
- Enable Google+ API for this domain, using Google's OAuth2 API dashboard
- Replace the client_secrets.json files in web app

## Third-Party References

### Login and SSH

- [ssh: connect to host X.X.X.X port 2200: Connection timed out](https://knowledge.udacity.com/questions/17016)
- [Log in with an SSH private key on Linux and Mac
](https://support.rackspace.com/how-to/logging-in-with-an-ssh-private-key-on-linuxmac/)
- [How do I add new user accounts with SSH access to my Amazon EC2 Linux instance?](https://superuser.com/questions/1221476/how-do-i-add-new-user-accounts-with-ssh-access-to-my-amazon-ec2-linux-instance)
- [How To Create a Sudo User on Ubuntu](https://linuxize.com/post/how-to-create-a-sudo-user-on-ubuntu/)

### Apache

- [How To Install Linux, Apache, MySQL, PHP (LAMP) stack on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu-16-04)
- [How To Install the Apache Web Server on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-16-04)

### Flask

- [mod_wsgi Quick Configuration Guide](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html)
- [Flask Deployment Options](http://flask.pocoo.org/docs/0.12/deploying/#deployment)
- [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
- [Deploying python Flask web app on Amazon Lightsail](https://umar-yusuf.blogspot.com/2018/02/deploying-python-flask-web-app-on.html)

### Git

- [How To Install Git on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu-16-04)

### PostgreSQL

- [Converting sqllite DB to postgres](https://knowledge.udacity.com/questions/26808)
- [How to create a new database using SQLAlchemy?](https://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy)
- [PostgreSQL 9.5.16 Documentation](https://www.postgresql.org/files/documentation/pdf/9.5/postgresql-9.5-US.pdf)
- [How To Use PostgreSQL with your Django Application on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04)
- [How to manage PostgreSQL databases and users from the command line](https://www.a2hosting.com/kb/developer-corner/postgresql/managing-postgresql-databases-and-users-from-the-command-line)


## Contributing

This is a class project. Pull requests will not be accepted.

