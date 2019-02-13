 Linux Server Configuration

## Table of Contents

- [Solution](#solution)
- [References](#references)
- [Contributing](#contributing)

## Solution

This is my solution to the "Configure Linux Server" project from Udacity's "Full Stack Web Developer" nanodegree course.

Here are the steps I took to convert the "Item Catalog" project from a locally-hosted debug app using a SQLite database to a real webapp running on an Apache server in the cloud using a PosgreSQL database.

### Set up an Apache server on AWS with SSH keys for 2 users

#### create an SSH key pair for the user `ubuntu`

- in Mac OS X Terminal app:
  - `cd ~`
  - `ssh-keygen`
  - name the files `ubuntu_key`, no passphrase
  - the two files are stored in `~ (/Users/keith)`

#### create an SSH key pair for the user `grader`

- follow previous step
- name the files `grader_key`

### Create an instance of Ubuntu on an AWS server

- Create an AWS account or sign into an existing one
- Create a new Lightsail image
- Pick Platform=Linux, Blueprint=OS only/Ubuntu 16.04
- When it asks about ssh key pair, upload ubuntu_key.pub
- Choose the cheapest instance plan
- Accept the default name in "Identify your Instance"
- CREATE INSTANCE
- When the instance has been created, connect to it using the web-based terminal on AWS website
- Note the public and private IP addesses:
  - Private IP: 172.26.6.50
  - Public IP: 34.220.98.225

### Get the server software up-to-date

Connect to Ubuntu using the web-based Terminal app:
- Update package lists, upgrade any apps that need it
  - sudo apt-get update
  - sudo apt-get upgrade
    - when prompted, type y
    - if you get the pink screen about /tmp/grub, hit enter
  - sudo apt-get autoremove
- Install finger and test it
  - sudo apt-get install finger
  - finger
- log out of web browser ssh connection

https://github.com/bcko/Ud-FS-LinuxServerConfig-LightSail

Note: the next few sections are informed by a post by Brian B in the
Udacity forums
https://knowledge.udacity.com/questions/17016
and an article on rackspace.com:
https://support.rackspace.com/how-to/logging-in-with-an-ssh-private-key-on-linuxmac/

### ssh into the Linux box from the Mac's Terminal app using Port 22

- On local Mac terminal:
  - find the private key file (ubuntu_key) that you created before (it should be in /Users/keith folder on Mac)
  - copy ubuntu and grader keys to .ssh on local machine
    - cp ~/ubuntu* ~/.ssh
    - cp ~/grader* ~/.ssh
  - chmod 600 ~/.ssh/ubuntu_key
  - chmod 600 ~/.ssh/grader_key
  - ssh -i ~/.ssh/ubuntu_key ubuntu@34.220.4.98.225
  - when it asks if it's ok to connect, type yes
  - You should now be logged into the Linux box

### Enable port 2200 for ssh

- In ubuntu terminal, edit config file
  - sudo nano /etc/ssh/sshd_config
  - add Port 2200 below Port 22 (don't delete port 22 yet)
  - write file and exit (Ctrl+O, Enter, Ctrl+X)

### Configure the server's firewall

- On Ubuntu terminal:
  - sudo ufw status					# should be "inactive"
  - sudo ufw default deny incoming	# deny access to all inbound ports
  - sudo ufw default allow outgoing # allow all outbound ports
  - sudo ufw allow 2200/tcp			# allow ssh on port 2200
  - sudo ufw allow www	  			# allow www on port 80
  - sudo ufw allow              # allow ntp on port 123
  - sudo ufw enable
  - sudo ufw status

### log into port 2200 on Ubuntu server

  - Ctrl+D to log out of server
  - reboot server using button on AWS website
  - check firewall settings on website (Networking tab)
    - if there's no port 2200 create one (Custom, TCP)
    - if there's no port 123 create one (Custom, TCP)
    - if there IS a poudo
    rt 22, delete it
  - ssh -i ~/.ssh/ubuntu_key ubuntu@34.220.4.56 -p 2200
  - remove "Port 22" from sshd_config:
    - sudo nano /etc/ssh/sshd_config

### Add a user named "grader" and give them sudo privileges

  On Ubuntu terminal:
  - sudo adduser grader
    - set pw to "fullstack"
    - set fullname to "Udacity Grader"
  - finger grader # to confirm

https://linuxize.com/post/how-to-create-a-sudo-user-on-ubuntu/
  - sudo usermod -aG sudo grader

### setup ssh key pair for "grader"

  - On Ubuntu terminal:
    - sudo su - grader
    - mkdir .ssh
    - chmod 700 .ssh
    - touch .ssh/authorized_keys
    - chmod 600 .ssh/authorized_keys

  - Open a local terminal on Mac:
    - cat /Users/keith/.ssh/grader_key.pub
    - select and copy the key, which looks like this:

Anoterh try:
https://superuser.com/questions/1221476/how-do-i-add-new-user-accounts-with-ssh-access-to-my-amazon-ec2-linux-instance


ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTvTnCzaaIPChWXgvxlyswcNzzTjlYUcfNExm6zGGJRtEcjvHMpV6vg9XMOb9ZgRNhgpWQqitQ9yLy+mjznDerfuK9RsEIdu5wb7uVFXs6TGHy8b9sqid0PH6PYuWiZ1/pA6cRrtQudeqlZuVV5wyimPFKZONW3v+BOp+AtIvChPhZI+rWn0T3vxi2NTHfdqW93VqsQ7ReEkzd1RGxJZ+1X0kADmCJKjwAoju0DvvVz3/xdsc2UT3rjRsUTxDR1bH4GBQr7U1pwCGAqZqvEl72TLpUdWRECG42qIPsut95c237gtzkwlU7iAOeiPWJduMV/bPxXnrB/YqF+XwRMuiz testuser@testEC2


On Ubuntu terminal
  - edit this file and paste in the key:
    - nano ~/.ssh/authorized_keys
  - paste the copied key into this file
  log out (Ctrl+D)
  Log into grader account:
  - ssh -i ~/.ssh/grader_key grader@34.220.98.225
   -p 2200
  -- verify it owrks
  - log out

### Prevent users from logging in with passwords
  - log into ubuntu account
    - ssh -i ~/.ssh/ubuntu_key ubuntu@34.220.98.225 -p 2200
  - sudo nano /etc/ssh/sshd_config
  - change "PasswordAuthentication" value to "no"
  - sudo service ssh restart
  [this is arleady done by Windsail]

### Prevent users from logging in as root
  - sudo nano /etc/ssh/sshd_config
  - change "PermitRootLogin" to "probinit-passeword" (already done in Ubuntu so we don't have to)
  - sudo service ssh restart
  [this is arleady done by Windsail]

### Change timezone to UTC
sudo dpkg-reconfigure tzdata

### set up a test mod_wagi project

### Install Apache

  - On Ubuntu terminal:
    - sudo apt-get update
    - sudo apt-get install apache2
    - set a flag to superess a warning:
      - sudo nano /etc/apache2/apache2.conf
      - add a line to bottom of file:
      ServerName server_domain_or_IP
    - check fors syntax errors
      - sudo apache2ctl configtest  # syntax OK
    - restart Apache
      - sudo systemctl restart apache2
  [firewall config?]
    - check IP address in browser
    - should see Apache/Ubuntu test page

### Install end enable mod_wsgi

  - sudo apt-get install libapache2-mod-wsgi python-dev
  - sudo a2enmod wsgi  # already enabled

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

*** install Flask

  install pip:
  - sudo apt-get install python-pip
<!--   install virtual environment
  - sudo pip install virtualenv
  Give the following command (where venv is the name you would like to give your temporary environment):
  - sudo virtualenv venv
  Now, install Flask in that environment by activating the virtual environment with the following command:
  - source venv/bin/activate
 -->  Give this command to install Flask inside:
  - sudo apt-get install  python-flask

  Next, run the following command to test if the installation is successful and the app is running:
  - sudo python __init__.py
It should display “Running on http://localhost:5000/” or "Running on http://127.0.0.1:5000/". If you see this message, you have successfully configured the app.

To deactivate the environment, give the following command:
  - deactivate

*** Configure and Enable a New Virtual Host
  - sudo nano /etc/apache2/sites-available/FlaskApp.conf

Paste this code into that file:

  <VirtualHost *:80>
      ServerName 34.220.98.225
      ServerAdmin admin@mywebsite.com
      WSGIScriptAlias / /var/www/flaskapp/flaskapp.wsgi
      <Directory /var/www/flaskapp/flaskapp/>
        Order allow,deny
        Allow from all
      </Directory>
      Alias /static /var/www/flaskApp/flaskapp/static
      <Directory /var/www/flaskApp/flaskapp/static/>
        Order allow,deny
        Allow from all
      </Directory>
      ErrorLog ${APACHE_LOG_DIR}/error.log
      LogLevel warn
      CustomLog ${APACHE_LOG_DIR}/access.log combined
  </VirtualHost>

save and close the filea

Enable the virtual host with the following command:
- sudo a2ensite FlaskApp

Disable the default Apache site
- sudo a2dissite 000-default
- sudo service apache2 reload

????????????????????????????????????????????????????????
Edit
/etc/hosts
 on your computer and add this line to the bottom:
34.220.4.56 flaskapp.dev
??????????????????????????????????????????????????????????

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

### restart apache
- sudo service apache2 restart
- sudo apachectl restart
- test, with a browser, that 34.220.4.56 calls up a Hello page

### Install git
sudo apt-get install git-core
git config --global user.name "J Keith Thomson"
git config --global user.email "jkthomson@gmail.com"

### now set up a similar arrangement for the Catalog app
- cd /var/www
- sudo clone https://jkeiththomson@github.com/jkeiththomson/catalog.git CatalogApp

=====================================

  - sudo a2enmod wsgi

======================================

### install and configure postgreSQK
sudo apt install python-postgresql postgres-contrib python-psycopg2

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
https://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy

https://www.google.com/search?q=install+github+on+ubuntu+16.04&oq=install+github+on+ubuntu&aqs=chrome.2.69i57j0l5.13422j0j4&sourceid=chrome&ie=UTF-8

http://flask.pocoo.org/docs/0.12/deploying/#deployment


https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-16-04


### install python and dependencies
sudo apt-get install python
sudo apt-get install python-pip
sudo apt-get install python-httplib2
sudo apt-get install python-sqlalchemy
sudo pip install sqlachemy_utils
sudo apt-get install python-requests
sudo apt-get install python-flask
sudo apt-get install python-h2client


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


### create and populate the inital database
 Make ubuntu a db user



### enable my website, remove default website

 Now, disable the default Apache site, enable your flask app, and then restart Apache for the changes to take effect. Run these commands to do this:

sudo a2dissite 000-default.conf
sudo a2ensite myApp.conf
sudo service apache2 reload

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

https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04


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
