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
# show status
docker ps 
# stop docker
docker stop $(docker ps -a -q)
docker-compose down
# rebuild no cache
docker-compose build --no-cache
# compose
docker-compose up
# docker permissions to container
docker exec -u root container_1 chmod 777 .
# inside container
sudo docker exec -it effb7bb0d048 /bin/bash

## VM commands
sudo -su root ## super user
rm -r -v Example ## remove dir
sudo -su root ## username
screen -X -S SCREENID kill

## update permissions
chmod -R 777 queen.pkl or dir client_user_dbs
sudo chmod 777 symbols_pollenstory_dbs -R
sudo chmod 777 symbols_STORY_bee_dbs -R

sudo chmod +rwx symbols_STORY_bee_dbs ## change permissions

## check for all python paths
export PYTHONPATH="${PYTHONPATH}:${HOME}/home/stapinski89/pollen/pollen"
python -c "import sys; print(sys.path)"


## Setting Up Sever
fastapi: uvicorn server:app --reload

Ngnix
docker >> Q: pythonpath missing?, airflow UID missing?

import os
directory = "/home/stapinski89/pollen/pollen/db/logs"
for file_path in os.listdir(directory):
    f_p = os.path.join(directory, file_path)
    os.chmod(f_p, 0o777)

requiements openai and transformers