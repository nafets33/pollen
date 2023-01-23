# Pollen

## Install ENV and pre-commit hooks
- pip install -r requirements.txt <<< may need fix >>>
- pre-commit install

## Commands to execute:
- streamlit run pollenq.py
- python QueenBee_sandbox.py
- python QueenBeeWorkerBees.py -prod False

## Docker
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose

run as >>> sudo -su root 
docker-compose up

docker ps # show status

## VM commands
rm -r -v Example ## remove dir
sudo -su root ## username

sudo chown stapinski89:stapinski89 symbols_pollenstory_dbs
sudo chown stapinski89:stapinski89 symbols_STORY_bee_dbs  # fix root
sudo chown stapinski89:stapinski89 client_user_dbs  # fix root

sudo chmod +rwx symbols_STORY_bee_dbs ## change permissions

