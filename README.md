# Pollen

## Install ENV and pre-commit hooks
- pip install -r requirements.txt <<< may need fix >>>
- pre-commit install

## upgrade Google VM
ensure to change IpAddress for google domain

## Run Locally  ## use folders from local_db_refence
Create following Dir Manually inside pollen/
symbols_pollenstory_dbs
symbols_STORY_bee_dbs
client_user_dbs

## Docker
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose

docker-compose build --no-cache

run as >>> sudo -su root 
docker-compose up
# show status
docker ps 
## stop docker
docker stop $(docker ps -a -q)


## VM commands
rm -r -v Example ## remove dir
sudo -su root ## username
screen -X -S SCREENID kill

## update permissions
chmod -R 777 queen.pkl or dir client_user_dbs

sudo chmod +rwx symbols_STORY_bee_dbs ## change permissions

## check for all python paths
export PYTHONPATH="${PYTHONPATH}:${HOME}/home/stapinski89/pollen/pollen"
python -c "import sys; print(sys.path)"


## Setting Up Sever
Ngnix
docker
