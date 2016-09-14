Subscriptions README
==================

Manual setup guide
----------------

# add VENV system variable
export VENV=/home/docker/code/env/

cd /home/docker/code/

# clone the source from git
git clone https://github.com/00riddle00/subscription_demo.git app/

cd app/

# initialize virtual environment
virtualenv -p python3.4 $VENV

# install setuptools
$VENV/bin/pip3 install --upgrade pip setuptools

# install all the packages by the pyramid app
$VENV/bin/python3.4 setup.py develop &&

# initialize database 
$VENV/bin/initialize_subscriptions_db development.ini &&

# run development server
$VENV/bin/pserve development.ini --reload'

# view the project 
[browser] http://localhost:6543

# a helpful alias to update and run the project
echo "
echo test >> subscriptions.sqlite &&
rm subscriptions.sqlite &&
$VENV/bin/python3.4 setup.py develop &&
$VENV/bin/initialize_subscriptions_db development.ini &&
$VENV/bin/pserve development.ini --reload'
" >> ~/.bashrc

# restart bash
bash

cd {{ path }}/app 

run

