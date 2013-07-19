# How to install ?


## Development environment (without Vagrant)

1. You should have installed *Python 2.7*, *pip* and *virtualenv*.
  
  Under Debian / Ubuntu, this should be as easy as:

          apt-get install python2.7 python-pip virtualenvwrapper 
  
  You might need to install additional dependencies such as:
          
          apt-get install libxml2-dev libxslt-dev libpq-dev python-dev

  On Mac OS with homebrew, you should install:

          brew install python
          brew pip install virtualenvwrapper

2. Type `mkvirtualenv owf` or 'virtualenv owf' (second parameter is the name of your cloned directory)

3. Type `pip install -r deps.txt` (you might need to run this command as root user, or with sudo)

4. Type `make run` and point your browser to the URL given by the logs (eg. http://0.0.0.0:5002/).


## Development environment (using Vagrant)

1. Install Vagrant (<http://www.vagrantup.com/>)

2. Run `vagrant up`

3. Run `vagrant ssh -c 'cd /vagrant ; make run'`

4. Point your browser to http://localhost:5002/

Every changes you do in the project file (on the host machine) should be 
available immediately on browser.


## Production environment

Not done yet.
