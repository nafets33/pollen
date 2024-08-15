# Pollen
Python == 3.9.9

## Create a Virtual ENV and pre-commit hooks
- pip install -r requirements.txt
- pre-commit install

## Run Locally  ## use folders from local_db_refence
-unzip the folder into pollen symbols_pollenstory_dbs.zip
-unzip the folder into pollen symbols_STORY_bee_dbs.zip
-unzip the folder into pollen client_user_dbs

## Create .env and setup variables
-APCA_API_KEY_ID = ""
-APCA_API_SECRET_KEY = ""
-APCA_API_KEY_ID_PAPER = ""
-APCA_API_SECRET_KEY_PAPER = ""
-admin_user = "your email"
# Preset Variables
fastAPI_key = "fastapi_pollenq_key"
fast_api_local_url = "http://127.0.0.1:8000"
cookie_name = "pollen_user_auth"
cookie_key = "pollen321"
cookie_expiry_days = "30"

## Run the App Locally // runs on local:8501
streamlit run pollen.py
python pollen_api.py

## After Running pollen.py
Create a New User
Use Verification Code 0

# Optional
pollenq_gmail = ""
pollenq_gmail_app_pw = ""
gcp_ip = ""
airflow_env = ""
airflow_host = ""
airflow_username = "airflow"
airflow_password = ""
AIRFLOW_UID=50000


### OPTIONAL USE DOCKER ###

## Docker
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose
# Docker Commands show status
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


## FOR VM: upgrade Google VM
ensure to change IpAddress for google domain