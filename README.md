# Generative AI Chatbot

## Agenda
* Build a chatbot using open source models - qroq or ollama via api
* Giving the chatbot memory - using mongo db
* creating an api for the chatbot deployment - using fastapi
* deploy chatbot using render

## Steps
* Create a folder on Github
* Clone the repo
* crate and activte a virutal enviroment either conda or pyenv
* create requirements.txt
* install the requirements.txt - pip install -r requirements.txt
* setup .env file

Accessing the open source models on Groq via api key
Go to the groq platform create and api key, copy it in the .env file

# Giving LLM Memory
* sign inot mongo db
* create a new project (eg give chat)
* create a cluster - select the region that is close to you
* copy the username and password and store in the .env file
* create database connection - select driver; copy the mongodb_uri and stop store it in .env


#### Creating Virtual Environment 
python3 -m venv .venv
source .venv/bin/activate
