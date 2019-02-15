 Linux Server Configuration

## Table of Contents

- [Solution](#solution)
- [References](#references)
- [Contributing](#contributing)

## Solution

This is my solution to the "Configure Linux Server" project from Udacity's "Full Stack Web Developer" nanodegree course.

Here are the steps I took to convert the "Item Catalog" project from a locally-hosted, debug website using a SQLite database to a real website running on an Apache server in the cloud using a PosgreSQL database.

### 1. Create SSH key pairs for two Ubuntu users

#### a. Create an SSH key pair for the user `ubuntu`:

In Mac OS X Terminal app:
- `cd ~`
- `ssh-keygen`
- Name the files `ubuntu_key`, no passphrase
- The two files are stored in `~ (/Users/keith)`

#### b. Create an SSH key pair for the user `grader`:

In Mac OS X Terminal app:
- Follow previous step
- Name the files `grader_key`

### 2. Create an instance of Ubuntu on an AWS server

#### a. Create the instance using Amazon Web Services

On AWS website:
- In a browser, navigate to https://aws.amazon.com/
- Create an AWS account or sign into an existing one
- Create a new Lightsail image
- Choose these options:
  - Instance location=Oregon Zone A
  - Platform=Linux/Unix
  - Blueprint=OS only/Ubuntu 16.04
  - SSH key pair: upload `ubuntu_key.pub` you made earlier
  - Instance plan=cheapest
  - Identify your instance=use the default name
- CREATE THE INSTANCE
- After the instance finishes being created (i.e. state goes rom Pendingto Running):
  - Select the instance by clicking its name
  - Click "Connect using SSH"
- Note the public and private IP addesses:
  - Private IP: 172.26.4.214
  - Public IP: 34.215.182.60

#### b. Get OS software up tp date

You should already be connected to Ubuntu image using the web-based terminal

In web-based terminal:
- Update package lists, upgrade any apps that need it
  - `sudo apt-get update`
  - `sudo apt-get upgrade`
    - when prompted, type y
    - if you get the pink screen about /tmp/grub, hit Enter
  - `sudo apt-get autoremove`
- Install finger and test it
  - `sudo apt-get install finger`
  - `finger`

#### c. Set time zone to UTC

On Ubuntu terminal:
- `sudo dpkg-reconfigure tzdata`
  - Select "None of the above"
  - Select "UTC"
- Log out of web browser SSH connection (Ctrl+D)

### 3. Set up SSH logins for our two users

#### a. Set up user `ubuntu`

On local Mac terminal:
- Find the private key file (`ubuntu_key`) that you created before (it should be in `/Users/<username>` folder on Mac)
- Copy `ubuntu` and `grader` keys to `.ssh` on local machine
  - `cp ~/ubuntu* ~/.ssh`
  - `cp ~/grader* ~/.ssh`
- `chmod 600 ~/.ssh/ubuntu_key`
- `chmod 600 ~/.ssh/grader_key`
- `ssh -i ~/.ssh/ubuntu_key ubuntu@34.215.182.60`
- When it asks if it's ok to connect, type yes
You should now be logged into the Linux box

#### b. Set up user `grader` and give them sudo privileges

On Ubuntu terminal:
- `sudo adduser grader`
  - set pw to "fullstack"
  - set fullname to "Udacity Grader"
  - just hit Enter for the rest of the parameters
- `finger grader` # to confirm
- Give them sudo privileges
  - `sudo usermod -aG sudo grader`

#### c. Set up ssh key pair for "grader"

On Ubuntu terminal:
  - `sudo su - grader`
  - `mkdir .ssh`
  - `chmod 700 .ssh`
  - `touch .ssh/authorized_keys`
  - `chmod 600 .ssh/authorized_keys`

Open a local terminal on Mac:
  - `cat /Users/<username>/.ssh/grader_key.pub`
  - Select and copy the key, which looks like this:
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTvTnCzaaIPChWXgvxlyswcNzzTjlYUcfNExm6zGGJRtEcjvHMpV6vg9XMOb9ZgRNhgpWQqitQ9yLy+mjznDerfuK9RsEIdu5wb7uVFXs6TGHy8b9sqid0PH6PYuWiZ1/pA6cRrtQudeqlZuVV5wyimPFKZONW3v+BOp+AtIvChPhZI+rWn0T3vxi2NTHfdqW93VqsQ7ReEkzd1RGxJZ+1X0kADmCJKjwAoju0DvvVz3/xdsc2UT3rjRsUTxDR1bH4GBQr7U1pwCGAqZqvEl72TLpUdWRECG42qIPsut95c237gtzkwlU7iAOeiPWJduMV/bPxXnrB/YqF+XwRMuiz testuser@testEC2

On Ubuntu terminal
- Edit the authorized keys file:
  - `nano ~/.ssh/authorized_keys`
- Paste the copied key into the file and save it
  - Ctrl+O, Enter, Ctrl+X
- Log out (Ctrl+D, Ctrl+D)
Log into grader account:
- ssh -i ~/.ssh/grader_key grader@34.215.182.60
- verify it works
- log out

### 4. Set up ports and firewall for Ubuntu

#### e. Enable port 2200 for ssh

On Ubuntu terminal, edit config file:
- `sudo nano /etc/ssh/sshd_config`
- Add Port 2200 below Port 22 (don't delete port 22 yet)
- Write file and exit (Ctrl+O, Enter, Ctrl+X)

#### b. Configure the server's firewall

On Ubuntu terminal:
- `sudo ufw status`					        # should be "inactive"
- `sudo ufw default deny incoming`	# deny access to all inbound ports
- `sudo ufw default allow outgoing` # allow all outbound ports
- `sudo ufw allow 2200/tcp`	    		# allow ssh on port 2200
- `sudo ufw allow www`	  			    # allow www on port 80
- `sudo ufw allow ntp`                  # allow ntp on port 123
- `sudo ufw enable`                 # enable firewall
- `sudo ufw status`                 # recheck status

#### c. Log into port 2200 on Ubuntu server

On Ubuntu terminal:
- Ctrl+D to log out of server
- Reboot server using button on AWS website
- Check firewall settings on AWS website (Networking tab)
  - if there's no port 2200 create one (Custom, TCP)
  - if there's no port 123 create one (Custom, TCP)
  - if there IS a port 22, delete it
  - Click Save
- `ssh -i ~/.ssh/ubuntu_key ubuntu@34.220.4.56 -p 2200`
- Remove "Port 22" from sshd_config:
  - `sudo nano /etc/ssh/sshd_config`

### 5. Set up some security precautions in Ubuntu

#### a. Prevent users from logging in with passwords

On Ubuntu terminal:
- Log into ubuntu account
  - `ssh -i ~/.ssh/ubuntu_key ubuntu@34.220.98.225 -p 2200`
- `sudo nano /etc/ssh/sshd_config`
- Change `PasswordAuthentication` value to `no`
- `sudo service ssh restart`
[this is already done by Windsail]

#### b. Prevent users from logging in as root

On Ubuntu terminal:
- `sudo nano /etc/ssh/sshd_config`
- Change `PermitRootLogin` value to `probinit-password`
- 'sudo service ssh restart'
[this is already done by Windsail]

### 6. Install all the software we will need

#### a. Install Apache

On Ubuntu terminal:
- `sudo apt-get update`
- `sudo apt-get install apache2`
- Set a flag to supress a warning:
  - `sudo nano /etc/apache2/apache2.conf`
  - add a line to bottom of file:
    - `ServerName <server_domain_or_IP>`
- Check for syntax errors
  - `sudo apache2ctl configtest`  # syntax OK
- Restart Apache
  - `sudo systemctl restart apache2`
  [firewall config?]
- check IP address in browser
  - sudo service apache2 restart
  - sudo apachectl restart
  - test, with a browser, by boing to 34.215.182.60
  - should see Apache2 Ubuntu Default Page

#### b. Install Python 2.7

On Ubuntu terminal:
- sudo apt-get install python
- sudo apt-get install python-pip
- sudo apt-get install python-httplib2
- sudo apt-get install python-requests
FOO - sudo apt-get install python-h2client

#### c. Install sqlalchemy

On Ubuntu terminal:
- sudo apt-get install python-sqlalchemy
- sudo pip install sqlachemy_utils

#### d. Install Flask

On Ubuntu terminal:
- `sudo apt-get install python-flask`

FOO Test Flask installation
  - 'sudo python __init__.py'
  - Console should say “Running on http://localhost:5000/” or "Running on http://127.0.0.1:5000/"

#### e. Install mod_wsgi

On Ubuntu terminal:
  - `sudo apt-get install libapache2-mod-wsgi python-dev`
  - `sudo a2enmod wsgi`  # should say "already enabled"

#### f. Install Git

On Ubuntu terminal:
- `sudo apt-get install git-core`
- `git config --global user.name "J Keith Thomson"`
- `git config --global user.email "jkthomson@gmail.com"`

#### g. Install postgresql

On Ubunto terminal:
- `sudo apt-get update`
- `sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib`
- `sudo pip install psycopg2-binary`

### 7. Get and deploy web app code

#### a. Get code from Github

On Ubuntu terminal:
- `cd /var/www`
- `sudo git clone https://jkeiththomson@github.com/jkeiththomson/catalog.git`

#### b. Set up configuration file for Flask project

On Ubuntu terminal:
- Edit the config file
  - `sudo nano /etc/apache2/sites-available/catalog.conf`
- Paste this code into that file:

```
<VirtualHost *:80>
    ServerName 34.215.182.60
    ServerAdmin admin@mywebsite.com
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- Save and close the file

#### d. Update the webapp to use PostGreSQL instead of SQL_Lite

Note: these changes were made already and merged into Git, so they don't need to be done now. They are listed only for completeness.

On Ubuntu terminal,
- Edit `__init__.py`
  - `cd /var/www/catalog/catalog`
  - `sudo nano __init__.py`
  - Verify that there is no code in this file, only a comment
- Edit `catalog.py`
  - `sudo nano catalog.py`
  - Verify that the `create_engine` code has been converted to postgresql:
    - engine = create_engine('postgresql://ubuntu:udacity@localhost/orchestra')
- Edit `catalog.wsgi`
  - `sudo nano ../catalog.wsgi`
  - Verify that the code in this file looks like this:
```
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog/")

from catalog import catalog
application = catalog.app

```
#### e. Set up database users

On Ubuntu terminal:
- `sodu su - postgres`
- `createuser --interactive --pwprompt`
  - Name of role: ubuntu
  - Password: udacity
  - Superuser? y
- `createuser --interactive --pwprommpt`
  - Name: catalog
  - Password: udacity
  - Superuser: no
  - Create Dbs: no
  - Create roles: no

#### e. Initialize the database

On Ubuntu terminal,
-  `cd/var/www/catalog/catalog`
- `sudo python database_setup.py`
  - Console should respond with "orchestra database has been set up"
- Verify that database is there:
  - `psql orchestra`
    - `\du`  # lists the users
    - `/d`   # lists the tables

### 8. Enable the new web app

#### a. Disable default app and enable our catalog app

On Ubuntu terminal:
- Enable the virtual host with the following command:
  - `sudo a2ensite catalog`
- Disable the default Apache site
  - `sudo a2dissite 000-default`
- Reload the server
  - `sudo service apache2 reload`

#### b. Test that web app is working

On Mac OS X:
- Fire up a browser (I used Chrome)
- Navigate to http://34.215.182.60
- Verify that the web app works





<!--   install virtual environment
  - sudo pip install virtualenv
  Give the following command (where venv is the name you would like to give your temporary environment):
  - sudo virtualenv venv
  Now, install Flask in that environment by activating the virtual environment with the following command:
  - source venv/bin/activate
 -->

To deactivate the environment, give the following command:
  - deactivate


????????????????????????????????????????????????????????
Edit
/etc/hosts
 on your computer and add this line to the bottom:
34.220.4.56 flaskapp.dev
??????????????????????????????????????????????????????????

### create a Flask app

  - cd /var/www
  - sudo mkdir flaskapp
  - cd flaskapp
  - sudo mkdir flaskapp
  - cd flaskapp
  - sudo mkdir static templates
  - sudo nano __init__.py
    add to file:

from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, I love Digital Drama!"
if __name__ == "__main__":
    app.run()

    save and close the file
### create the .wsgi file
Apache uses the .wsgi file to serve the Flask app:
- cd /var/www/flaskapp
- sudo nano flaskapp.wsgi

Add the following lines of code to the flaskapp.wsgi file:

#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/flaskapp/")

from flaskapp import app as application
application.secret_key = 'Add your secret key'

### now set up a similar arrangement for the Catalog app
- cd /var/www
- sudo clone https://jkeiththomson@github.com/jkeiththomson/catalog.git CatalogApp

=====================================

  - sudo a2enmod wsgi

======================================

<!-- PotgreSGL has asuper user  naemd postgres -- siwtch ot that
sudo su - postgres
psql # logs into postgresql
CREATE DATABASE foobar;
CREATE USER foo WITH PASSWORD 'bar';
ALTER ROLE foobar SET client_encoding TO 'utf8';
ALTER ROLE foobar SET default_transaction_isolation TO 'read committed';
ALTER ROLE foobar SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE foobar TO foo;
 -->

### get the Catalog app from GitHub
sudo chown -R ubuntu /var/www
cd /var/www
git clone https://jkeiththomson@github.com/jkeiththomson/catalog.git

## configure mod_wdgi
nano /var/www/fullstack/vagrant/catalog/myApp.wsgi
put these 3 lines in
import sys
sys.path.inset(0,"/var/www/fullstack/vagrant/catalog/myApp")
from application import app

### configure apache
sudo chown ubuntu /etc/apache2
cd /etc/apache2/sites-available
nano myApp.conf
ei=dit the abovre file, add

<VirtualHost *>
 ServerName example.com
 WSGIScriptAlias / /var/www/catalog/myApp.wsgi
 WSGIDaemonProcess hello
 <Directory /var/www/catalog>
  WSGIProcessGroup hello
  WSGIApplicationGroup %{GLOBAL}
   Order deny,allow
   Allow from all
 </Directory>
</VirtualHost>
><>




### enable my website, remove default website

 Now, disable the default Apache site, enable your flask app, and then restart Apache for the changes to take effect. Run these commands to do this:

sudo a2dissite 000-default.conf
sudo a2ensite myApp.conf
sudo service apache2 reload



- Use the xip	.io service to get a DNS name for the public IP address
  - 34.219.235.25.xip.io



XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

### To install and run the website:

- The project relies on a Vagrant virtual machine (VM) that was pre-setup by Udacity. Instructions for setting up the VM can be found here: https://www.udacity.com/wiki/ud088/vagrant. The VM is a Linux server that will serve up this project's website.
- In your own OS (not the VM), browse to GitHub and log into your personal GitHub account. Navigate to my repository for this project: https://github.com/jkeiththomson/fullstack-nanodegree-vm
- Clone the repository to your computer (see the instructions at https://www.udacity.com/wiki/ud088/vagrant)
- Maker sure you're on the "master" braanch
- cd into the .../vagrant/catalog folder
- Run the virtual machine (vagrant up) and log into it (vagrant ssh)
- **IMPORTANT!** To set up the website's database on the VM:
  - cd to /vagrant/catalog
  - run "python database_setup.py" to create the database ("orchestra.db")
  - run "python application.py" to start the server
- To see the project website
  - Fire up your browser of choice on your computer (not the VM)
  - Browse to http://localhost:5000

## Description

For this project I elected to create a database of the musical instruments found in a typical symphony orchestra. The "categories" are the sections of the orchestra and the "items" are the instruments.

Using the project website should be relatively self-explanatory. Choose a category on the left and choose an item on the right. You have to be logged in to create, modify or delete an item.

The app is marginally responsive at smaller screen sizes.

## Change Log

This is version 1.1 of the Item Catalog project. I made the following changes based on my reviewer's feedback in order to satisfy the project rubric:

- Code is now PEP8 compliant, as reported by a pycodestyle review

- Users can no longer leave field sblank when creating or editing items

- Users are now limited to editing and deleting only those items that they created

I made one additional change, based on a suggestion by the reviewer:

- database_setup.py now reads the database informaton from a JSON file instead of being hard-coded in the app

## Attributions

The text of the descriptions of sections and instruments are all taken from wikipedeia.org.

The photos are mostly taken from wikipedia.org. Hover the mouse over a photo to see its attribution credit.

All the new code is my own, based on snippets from the course materials.

There is one citation in styles.css for some css code I borrowed to show the photo captions.

## Contributing

This is a class project. We will not accept pull requests.


https://github.com/bcko/Ud-FS-LinuxServerConfig-LightSail

Note: the next few sections are informed by a post by Brian B in the
Udacity forums
https://knowledge.udacity.com/questions/17016
and an article on rackspace.com:
https://support.rackspace.com/how-to/logging-in-with-an-ssh-private-key-on-linuxmac/


YES! https://linuxize.com/post/how-to-create-a-sudo-user-on-ubuntu/

Anoterh try:
https://superuser.com/questions/1221476/how-do-i-add-new-user-accounts-with-ssh-access-to-my-amazon-ec2-linux-instance

https://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy

https://www.google.com/search?q=install+github+on+ubuntu+16.04&oq=install+github+on+ubuntu&aqs=chrome.2.69i57j0l5.13422j0j4&sourceid=chrome&ie=UTF-8

http://flask.pocoo.org/docs/0.12/deploying/#deployment


https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-16-04

https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html

*** https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps

*** https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu-16-04



https://umar-yusuf.blogspot.com/2018/02/deploying-python-flask-web-app-on.html

https://knowledge.udacity.com/questions/26808



if this works, you are ready to go back to the previous steps and remove port 22 from sshd_config and from AWS firewall settings.


https://github.com/bcko/Ud-FS-LinuxServerConfig-LightSail

\du


https://www.postgresql.org/files/documentation/pdf/9.5/postgresql-9.5-US.pdf

https://knowledge.udacity.com/questions/26808

YES!
https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04

YES
https://www.a2hosting.com/kb/developer-corner/postgresql/managing-postgresql-databases-and-users-from-the-command-line











