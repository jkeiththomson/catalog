# Linux Server Configuration

## Step-by-Step Instructions

### 1. Create SSH key pairs for two Ubuntu users

#### a. Create an SSH key pair for the user `ubuntu`:

In Mac OS X Terminal app on local machine:
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
- After the instance finishes being created (i.e. state goes from Pending to Running):
  - Select the instance by clicking its name
  - Click "Connect using SSH"
- Note the public and private IP addesses:
  - Private IP: 172.26.10.224
  - Public IP: 18.237.175.26

#### b. Get OS software up to date

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
- `ssh -i ~/.ssh/ubuntu_key ubuntu@18.237.175.26`
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
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCg7cJDOvtP0VDQu4yzUasHf1asBnR2ClR9TuD+NKosnGm833QSq0heX3fVGXp3p3qshrwdZMj248ABJ9TS4wqGFeFrCzvhr6ZNyblZcGoEMpn39yrEW4LBSIvE5k8x9+if4PmkruWcSWmXhDFVCNg5RXMvVz5msC68iBB7EBXfPb7mBCd/SDoKvbPTphwSjRDXMmBCryYmxtfiYpV4zKfds8n2sfRjSxDQdblGU1kTzFhl7kQ7MhBGhZs5Zq0tao5wOXMHmWbowAJkvG/w72zZvyLIqCL1Tui2YPGDM60ch0rv5YOrf5ipozsa4GABtakHpdV0/ri9IqOpVfR22qpz keith@Keiths-MacBook-Pro.local

On Ubuntu terminal
- Edit the authorized keys file:
  - `nano ~/.ssh/authorized_keys`
- Paste the copied key into the file and save it
  - Ctrl+O, Enter, Ctrl+X
- Log out (Ctrl+D, Ctrl+D)
Log into grader account:
- ssh -i ~/.ssh/grader_key grader@18.237.175.26
- verify it works
- log out

### 4. Set up ports and firewall for Ubuntu

#### e. Enable port 2200 for ssh

On Ubuntu terminal, edit config file:
- `ssh -i ~/.ssh/ubuntu_key ubuntu@18.237.175.26`
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

In browser:
- Reboot server using button on AWS website
- Check firewall settings on AWS website (Networking tab)
  - if there's no port 2200 create one (Custom, TCP)
  - if there's no port 123 create one (Custom, TCP)
  - if there IS a port 22, delete it
  - Click Save

On Ubuntu terminal:
- `ssh -i ~/.ssh/ubuntu_key ubuntu@18.237.175.26 -p 2200`
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
- Change `PermitRootLogin` value to `prohibit-password`
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

#### h. Install oauth2 client

On Ubuntu terminal:
- `sudo pip install oauth2client`

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
    ServerName 18.237.175.26
    ServerAdmin jkthomson@gmail.com
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
- Ctrl+D to log out as user potgres and return to user ubuntu

#### e. Initialize the database

On Ubuntu terminal,
-  `cd /var/www/catalog/catalog`
- `sudo python database_setup.py`
  - Console should respond with "orchestra database has been set up"
- Verify that database is there:
  - `psql orchestra`
    - `\du`  # lists the users
    - `/d`   # lists the tables
- Ctrl+D to log out of psql

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
- Navigate to http://18.237.175.26
- Verify that the web app works
- You won't be able to log in yet

### 9. Add Google+ log in to web app

#### a. Remove hard coded IP addresses, replace with domain name

On Mac OS X:
- Assign domain name to this IP address
  - I own the domain "incredibleduc.com" which is registeredwith Hover
  - Browse to hover.com and sign in
  - Change the A records for incredibleduc.com to point to 18.237.175.26

On Ubuntu terminal:
- Log in as user ubuntu
  - `ssh -i ~/.ssh/ubuntu_key ubuntu@18.237.175.26`
- Remove hard-coded IP addresses
  - `sudo nano /etc/apache2/apache2.conf`
  - change IP address at end of file to domain name:
    - `18.237.175.26` => `incredibleduc.com`
  - `sudo nano /etc/apache2/sites-available/catalog.conf`
  - change IP address in second line of file to domain name:
    - `18.237.175.26` => `incredibleduc.com`

#### b. Enable Google+ API for this domain

In a web browser:
- Go to https://console.developers.google.com/ and log in
- Create an OAuth 2.0 client ID for the catalog app
  - Application type = web application
  - Name = Full Stack Server Project
  - Authorized JavaScrip origins
    - http://incredibleduc.com
  - Authorized redirect URIs
    - http://incredibleduc.com/login
    - http://incredibleduc.com/gconnect
    - http://incredibleduc.com/orchestra
  - Click CREATE button
  - Click name of credential in Credentials tab
  - Download JSON file

Back on the Mac
- Rename the JSON file client_secrets.json and copy it over the file in catlog/catalog/client_secrets.json
- Open the JSON file in a text editor and cut the client ID
- Paste the client ID into templates/showlogin.html, overwriting the old client ID
- Commit these 2 files in Git and push them to the remote repo

On Ubuntu terminal:
- Pull the two new files down from the remote repo
- Reboot the server

That's it!

## Third-Party References

