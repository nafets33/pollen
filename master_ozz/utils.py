import streamlit as st

import speech_recognition as sr
import time 
from dotenv import load_dotenv
import os
import pickle
import time
from datetime import datetime
import streamlit as st
import pandas as pd
import socket
import ipdb
import sys
import json
import random
import requests 
from PIL import Image

from elevenlabs import set_api_key
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import save

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import  UnstructuredMarkdownLoader, UnstructuredWordDocumentLoader, PyPDFLoader, PythonLoader, CSVLoader, TextLoader, UnstructuredHTMLLoader, UnstructuredExcelLoader
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from langchain.prompts import PromptTemplate
import openai

import argparse

from pydub import AudioSegment

from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder

from bs4 import BeautifulSoup
import re
from streamlit_extras.switch_page_button import switch_page
import hashlib

import boto3
from botocore.exceptions import NoCredentialsError

# import replicate ### ??????
import replicate as rp

import subprocess
from chess_piece.pollen_db import PollenDatabase

pg_migration = os.getenv('pg_migration')

# from youtubesearchpython import *
#### AUTH UTILS #####

def hash_string(string):
    # Hash the string
    hashed_string = hashlib.sha256(string.encode()).hexdigest()
    # Convert the hash to an integer ID
    id = int(hashed_string, 16) % (10 ** 8)
    return id


def init_user_session_state(prod, db_root, init_sessstate=True):
    if pg_migration:
        table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
        data = PollenDatabase.retrieve_data(table_name, f'{db_root}-SESSION_STATE')
        if 'hh_vars' not in data.keys():
            data['hh_vars'] = hoots_and_hootie_vars()
        
        if init_sessstate:
            for k,v in data.items():
                st.session_state[k] = v

        return data
    
    ss_file  = os.path.join(st.session_state['db_root'], 'session_state.json')
    st.session_state['ss_file'] = ss_file
    ss_data = load_local_json(ss_file)
    for k,v in ss_data.items():
        st.session_state[k] = v
    
    return ss_data

#### AUTH UTILS #####

# search_google_images, define when to set true and when it does it will display the images in slider form auto flipping each image every 3 seconds until user clicks and then it will stop slider from moving


def ozz_master_root(info='\ozz\ozz'):
    script_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(script_path)) # \pollen\pollen

def ozz_master_root_db(info='\ozz\ozz\ozz_db'):
    script_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(os.path.dirname(script_path)), 'ozz_db')


def init_constants():
    ROOT_PATH = ozz_master_root()
    OZZ_DB = ozz_master_root_db()
    DATA_PATH = f"{OZZ_DB}/DATA"
    PERSIST_PATH = f"{OZZ_DB}/STORAGE"
    OZZ_db_audio = f"{OZZ_DB}/audio"
    OZZ_db_images = f"{OZZ_DB}/images"
    OZZ_BUILD_dir = f"{ROOT_PATH}/custom_voiceGPT/frontend/build"

    data_paths = {'DATA_PATH': DATA_PATH,
            'PERSIST_PATH':PERSIST_PATH,
            'OZZ_BUILD_dir': OZZ_BUILD_dir,
            "OZZ_db_audio": OZZ_db_audio,
            "OZZ_db_images": OZZ_db_images,
            "ROOT_PATH": ROOT_PATH,
            "OZZ_DB": OZZ_DB,}
    for k,v in data_paths.items():
        st.session_state[k] = v
    
    return data_paths

ROOT_PATH = ozz_master_root()
OZZ_DB = ozz_master_root_db()

constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSIST_PATH')
OZZ_BUILD_dir = constants.get('OZZ_BUILD_dir')
OZZ_db_audio = constants.get('OZZ_db_audio')
OZZ_db_images = constants.get('OZZ_db_images')


load_dotenv(os.path.join(ozz_master_root(),'.env'))
set_api_key(os.environ.get("api_elevenlabs"))


def text_audio_fields(file_path, text, user_query=None, self_image=None, s3_filepath=None):
    if not self_image:
        self_image = file_path.split("/")[-1].split(".")[0] # name of file without extension

    return {'file_path': file_path, 
            'text': text, 
            'self_image': self_image,
            'datetime': datetime.now().strftime("%B %d, %Y %H:%M"),
            'user_query': user_query,
            's3_filepath': s3_filepath,}

def text_image_fields(file_path, text, user_query=None, self_image=None):
    if not self_image:
        self_image = file_path.split("/")[-1].split(".")[0] # name of file without extension

    return {'file_path': file_path, 
            'text': text, 
            'self_image': self_image,
            'datetime': datetime.now().strftime("%B %d, %Y %H:%M"),
            'user_query': user_query}

def load_local_json(file_path):
    
    with open(file_path, 'r') as filee:
        data = json.load(filee)
        
    return data

def save_json(db_name, data, log=True):
    # if pg_migration:
    #     up = PollenDatabase.upsert_data(data.get('table_name'), data.get('key'), data)
    #     return up
    
    if db_name:
        with open(db_name, 'w') as file:
            json.dump(data, file)
        if log:
            print(f'{db_name} saved')

def init_text_audio_db(db_name='master_text_audio.json'):
    master_text_audio_file_path = os.path.join(OZZ_DB, db_name)
    if os.path.exists(master_text_audio_file_path):
        master_text_audio = load_local_json(master_text_audio_file_path)
        return db_name, master_text_audio
    
    print("INIT DB")
    audio_db = os.path.join(OZZ_DB, 'audio')
    master_text_audio = []
    for audio in os.listdir(audio_db):
        try:
            audio_source = os.path.join(audio_db, audio)
            text = transcribe_audio_mp3(audio_source)
            input_save = text_audio_fields(audio_source, text)
            master_text_audio.append(input_save)
        except Exception as e:
            print_line_of_error(e)
    
    save_json(master_text_audio_file_path, master_text_audio)

    return db_name, master_text_audio


def init_text_image_db(db_name='master_text_image.json'):
    file_path = os.path.join(OZZ_DB, db_name)
    if os.path.exists(file_path):
        master_text_image = load_local_json(file_path)
        return master_text_image
    else:
        master_text_image = {'source': file_path, 'data': []}

    return master_text_image

def ReadPickleData(pickle_file):
    # Check the file's size and modification time
    prev_size = os.stat(pickle_file).st_size
    prev_mtime = os.stat(pickle_file).st_mtime
    stop = 0
    e = None
    while True:
        # Get the current size and modification time of the file
        curr_size = os.stat(pickle_file).st_size
        curr_mtime = os.stat(pickle_file).st_mtime

        # Check if the size or modification time has changed
        if curr_size != prev_size or curr_mtime != prev_mtime:
            pass
            # print(f"{pickle_file} is currently being written to")
            # logging.info(f'{pickle_file} is currently being written to')
        else:
            try:
                with open(pickle_file, "rb") as f:
                    pf = pickle.load(f)
                    pf['source'] = pickle_file
                    return pf
            except Exception as e:
                print('pkl read error: ', os.path.basename(pickle_file), e, stop)
                # logging.error(f'{e} error is pickle load')
                if stop > 3:
                    print("CRITICAL read pickle failed ", e)
                    # logging.critical(f'{e} error is pickle load')
                    # send_email(subject='CRITICAL Read Pickle Break')
                    return ''
                stop += 1
                time.sleep(0.033)

        # Update the previous size and modification time
        prev_size = curr_size
        prev_mtime = curr_mtime

        # Wait a short amount of time before checking again
        time.sleep(0.033)


def PickleData(pickle_file, data_to_store):
    if pickle_file:
        if len(data_to_store) > 0:
            with open(pickle_file, "wb+") as dbfile:
                pickle.dump(data_to_store, dbfile)
        else:
            return False
    else:
        return False

    return True


def print_line_of_error(e='print_error_message'):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(e, exc_type, exc_tb.tb_lineno)
    return exc_type, exc_tb.tb_lineno


def transcribe_audio_mp3(audio_file_path):
    recognizer = sr.Recognizer()

    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_file_path)

    # Convert audio to a compatible format (16-bit PCM WAV)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # Export the audio to a temporary WAV file
    temp_wav_file = "temp.wav"
    audio.export(temp_wav_file, format="wav")

    with sr.AudioFile(temp_wav_file) as source:
        audio_data = recognizer.record(source)

    # Transcribe the audio
    try:
        transcribed_text = recognizer.recognize_google(audio_data)
        return transcribed_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")

    return None


def append_audio(input_file1, input_file2, output_file):
    # Load audio segments
    audio_segment1 = AudioSegment.from_file(input_file1)
    audio_segment2 = AudioSegment.from_file(input_file2)

    # Concatenate audio segments
    final_audio = audio_segment1 + audio_segment2

    # Export the concatenated audio to a file
    final_audio.export(output_file, format="mp4")  #


def base_content():
    def content_type(name, url, tags):
        return {name, url, tags}

    main_return = {
        'youtube': [content_type(name='sleeping beatuy', url='https://www.youtube.com/watch?v=-DHqDPVezRc', tags={}),
                    content_type(name='snow white', url='https://www.youtube.com/watch?v=W8EXJ8Gqf0c', tags={})
                    ]
    }

    return main_return


def save_audio(filename, audio, response, user_query, self_image=False, db_name='master_text_audio.json', s3_filepath=None):
    try:
        ## all saving should happen at end of response return WORKERBEE
        master_text_audio_file_path, master_text_audio = init_text_audio_db()
        master_text_audio.append(text_audio_fields(filename, response, user_query, self_image, s3_filepath))
        save_json(master_text_audio_file_path, master_text_audio)

        local_path = filename=os.path.join(OZZ_db_audio, filename) 
        save(
            audio=audio,               # Audio bytes (returned by generate)
            filename=local_path                # Filename to save audio to (e.g. "audio.wav")
        )
        
        #upload to s3 bucket
        print("FIX Master DB FIRST before s3 upload")
        # upload_to_s3(local_file=local_path, bucket='ozzz', s3_file=s3_filepath)

        # del file?

        return local_path
    except Exception as e:
        print_line_of_error(e)
        return False

def generate_audio(query="Hello Story Time Anyone?", voice_id='zrHiDhphv9ZnVXBqCLjz', use_speaker_boost=True, 
                   settings_vars={'stability': .71, 'similarity_boost': .5, 'style': 0.0}, model_id='eleven_monolingual_v1'):
    try:
        # 'eleven_monolingual_v1' # eleven_multilingual_v2, eleven_turbo_v2
        # 'Mimi', #'Charlotte', 'Fin'
        audio = generate(
            model=model_id,
            text=query,
            # voice=voice,
            voice=Voice(
            voice_id= voice_id, #'zrHiDhphv9ZnVXBqCLjz', # mimi
            settings=VoiceSettings(stability=settings_vars.get('stability'), 
                                   similarity_boost=settings_vars.get('stability'), 
                                   style=settings_vars.get('style'), 
                                   use_speaker_boost=use_speaker_boost)
            ),
        )

        return audio
    except Exception as e:
        print_line_of_error(e)
        return None

def conversational_phrases(your_name, Hobby, Interest, Location, City, Place):

    conversational_phrases = {
        # Group 1: Greetings
        {"greeting_1": "Hello"},
        {"greeting_2": "Hi there"},
        {"greeting_3": "Hey"},
        {"greeting_4": "Good morning"},
        {"greeting_5": "Good afternoon"},
        {"greeting_6": "Good evening"},
        {"greeting_7": "How's it going?"},
        {"greeting_8": "Hey, what's up?"},
        {"greeting_9": "Yo!"},
        {"greeting_10": "Greetings"},

        # Group 2: Farewells
        {"farewell_1": "Goodbye"},
        {"farewell_2": "See you later"},
        {"farewell_3": "Take care"},
        {"farewell_4": "Farewell"},
        {"farewell_5": "Until next time"},
        {"farewell_6": "Catch you later"},
        {"farewell_7": "Have a great day!"},
        {"farewell_8": "Bye for now"},
        {"farewell_9": "Adios"},
        {"farewell_10": "So long"},

        # Group 3: Thanks
        {"thanks_1": "Thank you"},
        {"thanks_2": "Thanks a lot"},
        {"thanks_3": "I appreciate it"},
        {"thanks_4": "You're a lifesaver"},
        {"thanks_5": "Much obliged"},
        {"thanks_6": "I owe you one"},
        {"thanks_7": "Thanks a million"},
        {"thanks_8": "You rock"},
        {"thanks_9": "Gracias"},
        {"thanks_10": "I'm grateful"},

        # Group 4: Apologies
        {"apology_1": "I'm sorry"},
        {"apology_2": "My apologies"},
        {"apology_3": "I didn't mean that"},
        {"apology_4": "Forgive me"},
        {"apology_5": "I messed up"},
        {"apology_6": "It's my fault"},
        {"apology_7": "Please accept my apology"},
        {"apology_8": "I'm in the wrong"},
        {"apology_9": "I feel bad about it"},
        {"apology_10": "I regret that"},

        # Group 5: Introduction
        {"introduction_1": "My name is f'{your_name}'"},
        {"introduction_2": "I'm f'{your_name}'"},
        {"introduction_3": "Nice to meet you, I'm f'{your_name}'"},
        {"introduction_4": "Allow me to introduce myself, I'm f'{your_name}'"},
        {"introduction_5": "I go by f'{your_name}'"},
        {"introduction_6": "Hi, I'm f'{your_name}'"},
        {"introduction_7": "Pleased to make your acquaintance, I'm f'{your_name}'"},
        {"introduction_8": "Call me f'{your_name}'"},
        {"introduction_9": "I'm f'{your_name}', and I'm here to assist you"},
        {"introduction_10": "Greetings, I'm f'{your_name}'"},

        # Group 6: Interests
        {"interests_1": "I like f'{Hobby}'"},
        {"interests_2": "I'm interested in f'{Topic}'"},
        {"interests_3": "One of my hobbies is f'{Hobby}'"},
        {"interests_4": "I have a passion for f'{Interest}'"},
        {"interests_5": "In my free time, I enjoy f'{Hobby}'"},
        {"interests_6": "I'm a fan of f'{Interest}'"},
        {"interests_7": "I love to f'{Hobby}'"},
        {"interests_8": "One of my favorite things to do is f'{Hobby}'"},
        {"interests_9": "I'm into f'{Interest}'"},
        {"interests_10": "I'm a f'{Hobby}' enthusiast"},

        # Group 7: Location
        {"location_1": "I'm from f'{Location}"},
        {"location_2": "I live in f'{City}'"},
        {"location_3": "I'm based in f'{Place}'"},
        {"location_4": "My hometown is f'{Location}"},
        {"location_5": "I call f'{City}' my home"},
        {"location_6": "I reside in f'{Place}'"},
        {"location_7": "You can find me in f'{Location}"},
        {"location_8": "I'm currently in f'{City}'"},
        {"location_9": "I'm a native of f'{Location}"},
        {"location_10": "I'm located in f'{Place}'"},
    }

    charcters = ['mimi', 'fin']
    main_root = ozz_master_root()
    charcter_dirs = os.listdir(os.path.join(main_root, 'utils/character_db'))
    for charcter in charcters:
        for k_ey, convo in conversational_phrases.items():
            if charcter not in charcter_dirs:
                os.mkdir(charcter)
            
            filename = os.path.join(charcter, f'{charcter}{k_ey}.wav')

            audio = generate(
            text=convo,
            stream=False,
            voice= 'Fin', #'Charlotte', 'Fin'
            )
            save(
                audio=audio,               # Audio bytes (returned by generate)
                filename=filename               # Filename to save audio to (e.g. "audio.wav")
            )


def common_phrases_for_Questions():
    return [
    "What time",
    "Where are",
    "Can I",
    "How many",
    "Is it",
    "Do you",
    "Who is",
    "Why did",
    "Will you",
    "Are we",
    "Could you",
    "When will",
    "Should I",
    "Did you",
    "Would you",
    "Have you",
    "May I",
    "Are they",
    "Is there",
    "Do we",
    "Can we",
    "How much",
    "Should we",
    "Where is",
    "Will it",
    "Did he",
    "Who are",
    "Can you",
    "Could I",
    "Have we",
    "Did she",
    "Will they",
    "Would he",
    "When did",
    "Should they",
    "Is he",
    "Are you",
    "Where can",
]

def page_line_seperator(height="3", border="none", color="#C5B743"):
    return st.markdown(
        """<hr style="height:{}px;border:{};color:#333;background-color:{};" /> """.format(
            height, border, color
        ),
        unsafe_allow_html=True,
    )

def set_streamlit_page_config_once():
    try:
        main_root = ozz_master_root()

        jpg_root = os.path.join(main_root, "misc")
        queenbee = os.path.join(jpg_root, "hootsAndHootie.png")
        page_icon = Image.open(queenbee)
        st.set_page_config(
            page_title="Ozz",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state='collapsed',
            #  menu_items={
            #      'Get Help': 'https://www.extremelycoolapp.com/help',
            #      'Report a bug': "https://www.extremelycoolapp.com/bug",
            #      'About': "# This is a header. This is an *extremely* cool app!"
            #  }
        )            
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            # ignore this error
            return True
        raise e


def run_pq_fastapi_server():

    script_path = os.path.join(ozz_master_root(), 'ozz_api.py')

    try:
        # Use sys.executable to get the path to the Python interpreter
        python_executable = sys.executable
        subprocess.run([python_executable, script_path, '-i'])
    except FileNotFoundError:
        print(f"Error: Python interpreter not found. Make sure Python is installed.")
    except Exception as e:
        print(f"Error: {e}")

def check_fastapi_status(ip_address):
    try:

        req = requests.get(f"{ip_address}/api/data/", timeout=2) # http://127.0.0.1:8000/api/data/

        return True
    # except ConnectionError as e:
    except Exception as e:
        print(e)
        return False

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


def return_app_ip():
    ip_address = st.session_state.get('ip_address')
    streamlit_ip=os.environ.get('streamlit_ip'), 
    # ip_address=os.environ.get('local_fastapi_address')
    
    if ip_address:
        return ip_address, streamlit_ip
    else:
        ip_address = get_ip_address()
    
    if ip_address == os.environ.get('gcp_ip'):
        # print("IP", ip_address, os.environ.get('gcp_ip'))
        ip_address = "https://api.divergent-thinkers.com"
        streamlit_ip = ip_address
    else:
        ip_address = os.environ.get('local_fastapi_address')

    st.session_state['ip_address'] = ip_address
    st.session_state['streamlit_ip'] = streamlit_ip

    return ip_address, streamlit_ip


def LoadMultipleFiles(files):
    extension = files.split(".")[-1]
    if extension == 'pdf':
        data = PyPDFLoader(files)
        pages = data.load()
        return pages
    elif extension == 'csv':
        data = CSVLoader(files)
        pages = data.load()
        return pages
    elif extension == 'md':
        data = UnstructuredMarkdownLoader(files)
        pages = data.load()
        return pages
    elif extension == 'docx' or extension == 'doc':
        data = UnstructuredWordDocumentLoader(files)
        pages = data.load()
        return pages
    elif extension == 'html':
        data = UnstructuredHTMLLoader(files)
        pages = data.load()
        return pages
    elif extension == 'xlsx' or extension == 'xls':
        data = UnstructuredExcelLoader(files)
        pages = data.load()
        return pages
    elif extension == 'py':
        data = PythonLoader(files)
        pages = data.load()
        return pages
    elif extension == 'txt':
        data = TextLoader(files)
        pages = data.load()
        return pages
    else:
        return None
    

# Function to load all the files and append them into a single documents
def Directory(directory : str):
    documents = []
    for file_path in os.listdir(directory):
        file_path = os.path.join(directory, file_path)
        document = LoadMultipleFiles(file_path)
        if document:
            documents.append(document)
        else:
            print("ERROR: ", file_path)
    return documents


#Function to create chunks of documents
def CreateChunks(documents : str, chunk_size=500, chunk_overlap=20):
    chunks = []
    for docs in documents:
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
        )
        chunk = text_splitter.split_documents(docs)
        chunks.extend(chunk)
    return chunks


# Function to create embeddings
def CreateEmbeddings(textChunks :str ,persist_directory : str):
    # Check if persist directory exists otherwise create it
    if not os.path.exists(persist_directory):
            os.mkdir(persist_directory)
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = FAISS.from_documents(documents=textChunks, embedding=embeddings)
    vector_store.save_local(persist_directory)
    return vector_store

def get_last_eight(lst=[], num_items=3):
    if len(lst) <= 1:
        return lst

    max_items = min(len(lst), num_items)

    return [lst[0]] + lst[-(max_items - 1):]


def handle_prompt(characters, self_image, conversation_history, main_prompt=None, system_info=False):
    try:
        
        self_image_name = self_image.split('.')[0]
        main_prompt = characters[self_image_name].get('main_prompt')
        
        if len(conversation_history) == 0: # FIRST ASK
            conversation_history.append({"role": "system", "content": main_prompt})
        
        if system_info:
            main_prompt = conversation_history[0].get('content')
            conversation_history[0] = {"role": "system", "content": main_prompt + system_info}
        else:
            conversation_history[0] = {"role": "system", "content": main_prompt}

        return conversation_history
    except Exception as e:
        print_line_of_error(e)



def llm_assistant_response(conversation_history):

    # response = Retriever(message, PERSIST_PATH)
    s = datetime.now()
    try:
        # conversation_history.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-4o", # gpt-3.5-turbo
            messages=conversation_history,
            api_key=os.getenv('ozz_api_key')
        )
        assistant_reply = response.choices[0].message["content"]
        print('LLM Call:', (datetime.now() - s).total_seconds())

        return assistant_reply
    except Exception as e:
        print_line_of_error(e)


# Function to fetch the answers from FAISS vector db 
def Retriever(query : str, persist_directory : str, search_kwards_num=8, score_threshold=.6, return_only_text=False):
    try:

        s = datetime.now()

        embeddings = OpenAIEmbeddings(api_key=os.environ.get('ozz_api_key'))
        # memory = ConversationBufferMemory()
        # embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vectordb = FAISS.load_local(persist_directory,embeddings=embeddings)
        retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={'score_threshold': score_threshold,
                                                                            "k": search_kwards_num})
        if return_only_text:
            docs = retriever.get_relevant_documents(query)
            return docs
        
        # For OpenAI ChatGPT Model
        qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model='gpt-4o',max_tokens=10000), chain_type='stuff', retriever=retriever, return_source_documents=True, openai_api_key=os.environ.get('ozz_api_key'))

        result = qa_chain({"query": query})

        print('retervier:', (datetime.now() - s).total_seconds())

        return result
    except Exception as e:
        print_line_of_error(e)


def MergeIndexes(db_locations : list, new_location : str = None):
    embeddings = OpenAIEmbeddings()
    """taking first database for merging all the databases
        so that we can return a single database after merging"""
    

    dbPrimary = FAISS.load_local(db_locations[0],embeddings=embeddings)
    for db_location in db_locations:
        if db_location == db_locations[0]:
            # if again we got first database then we skip it as we already have marked it as primary
            continue
        dbSecondary = FAISS.load_local(db_location,embeddings=embeddings)
        dbPrimary.merge_from(dbSecondary)

    # Return the merged database or we can store it as new db name as well 
    # dbPrimary.save_local(new_location)  Location where we have to save the merged database  
    return dbPrimary.docstore._dict


def ozz_characters(population=['stefan', 'hootsAndHootie', 'viki']): # class
    my_characters = {}
    def char_attributes(split_query_by, voice_id, main_prompt, conv_rules):
        return {'split_query_by':split_query_by, 'voice_id':voice_id, 
                'main_prompt':main_prompt, 
                'conv_rules': conv_rules}
    # voice_ids = {'stefan': 'L3J0wKSts5TjObrEafQa', 'mimi': 'zrHiDhphv9ZnVXBqCLjz'}
    for char in population:
        if char == 'stefan':
            split_query_by=['stefan', 'stephen', 'stephanie', 'stephan']
            voice_id = 'L3J0wKSts5TjObrEafQa'
            # main_prompt = # this really shoudl be groups, nice, safety like how to create a main prompt
            main_prompt = """
            You are Stefan Stapinski's current conscienceness and the context provided is information about stefan, Use this context information to speak on behalf of Stefan in the 1st person. 
            Never Lie and do not make up anything, if you do not know the answer, say that you don't know or having trouble getting that information.
            Each Response is also being spoken by Stefan's real voice, which he cloned using Eleven Labs.
            Be nice and sound calm and cool.
            Don't ask how you may be of assistance or how you can assist.
            Try to respond with less then 500 characters but if more detailed is required you can exceed but only up to a max of 1000 characters. 
            Do not repeat the users question back unless you are questioning them about the question.
            """
            conv_rules={}
        elif char == 'hootsAndHootie':
            split_query_by=['hey hoots', 'hey hootie', 'hoots']
            voice_id = 'zrHiDhphv9ZnVXBqCLjz'
            main_prompt = """
            Your name is Hoots, you are an owl and you're in school learning about the world.
            You specialize in kids development and story telling, you are learning to become an educator.
            If you don't know an answer or unsure you're answer is correct, ask for help, Victoria or Nadiya are typically around the store, and call out there names to help the customer, example, Nadiya, Victoria could you please help our friend here.
            You love to tell stories and hang out with your favorite owl family, Hootie. She is the greatest Owl is the world.
            You love to have a cup of tea, the british way, sit down with anyone who may be around and tell stories. Please always tell short stories for little kids.
            Please do not say you're an AI assistant, you are a smart owl.
            You have a great sense of sarcastic humor and you use it well in conversation.
            You believe is good and moral virture for all.
            Please keep your reponses short and clear, Try to Answer is less then 300 characters.
            """
            conv_rules={}

        elif char == 'viki':
            split_query_by=['hey viki', 'hey vic', 'hey vicky', 'hey vicki']
            voice_id = '9BWtsMINqrJLrRacOk9x'
            main_prompt = """

Your name is Vicki, you are a professional tutor, teaching russian speakers learn how to speak english.
Your students name is Victoria, you are helping her prep for a interview with DLI (DLI stands for Defense Language Institute) to teach the army students how to speak Russian.

Help listen to her responses in engligh and do your best to correct her sentences and ensure she learns properly.
Your Student is a beginner in english, so do not use complex words or sentenses, keep your responses simple and short. 

-Interview questions to ask Victoria
1. Why do you want to work for DLI?
2. How much experience do you have teaching russian?
3. What do you do if a student is not listening?
4. What prepared you for this job?
5. What do you do is a student is not learning the russian language well?
6. How do you feel about moving to California?
7. What would you do if one student insults another student in class?
8. How did you find out about this job?
9. What do you think about technology in the world?
10. What programs, technologies have you used?
11. How would you motivate students?

-Some answers to help for those questions
1. I want to work for the Army at DLI because I like teaching Russian and want to help soldiers learn. 
2. Several years of work in High school and Middle school and I worked as a tutor
3. Remind them we are in class. Focus on topic in class, and then talk to the student afterwards. If it doesn't help, I would ask my Supervisor for help.
4. Master's degree in Russian, years of work with Middle and High school students, and I worked as a tutor for many years.
5. I would try to explain what they don't understand more. I would find out about their interests and give them assignments based on those interests.
6. I like California. Monterey is beautiful. My children are moving there soon too.
7. I would focus on the topic in class, ask the student to stop, and talk to them after class. It is the army, I am sure you have rules - I would follow them. As a lawyer, I know how to follow rules.
9. Technology is growing and developing, it's very important and can be very helpful in teaching too. It can make classes more fun and more interactive. 
10. Microsoft Word, Power Point for presentations, Zoom, Google
11. I will do my best to tell them how important learning Russian is. I would find out about their interests and focus assignmnets on them. I would talk about interesting news and cultural events in the world. 

-Note
If her answer is good please ask another one of the interview questions.
If you don't understand the query from the user try move forward with practicing the interview and ask the interview questions. 

"""


        my_characters[char] = char_attributes(split_query_by, voice_id, main_prompt, conv_rules)

    return my_characters

def refreshAsk_kwargs(color_dict={'background_color_chat': 'transparent'}, header_prompt=''):
    return {'color_dict': color_dict, header_prompt: header_prompt}

def ozzapi_script_Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-ip', default='127.0.0.1')
    parser.add_argument ('-port', default='8000')
    return parser

# TRAINING FUNCTIONS #

def is_html(data):
    # Use BeautifulSoup to check if the data is HTML
    try:
        soup = BeautifulSoup(data, 'html.parser')
        return soup.html is not None
    except:
        return False

def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.get_text()
    return text_content

def clean_text(text):
    # Remove non-alphanumeric characters and extra whitespaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned_text = re.sub(' +', ' ', cleaned_text)  # Remove extra whitespaces
    return cleaned_text

def clean_data(data):
    if is_html(data):
        # If it's HTML, clean the HTML content first
        cleaned_text = clean_html(data)
        # Then, clean the text
        cleaned_text = clean_text(cleaned_text)
        return cleaned_text
    else:
        # If it's not HTML, just clean the text
        return clean_text(data)

def preprocessing(df): # df must be set as key content columns >> File name, contents
    #Removing unwanted characters
    for i in range(df.shape[0]):
        df['contents'][i] = df['contents'][i].replace('\n', '')
        df['contents'][i] = re.sub(r'\(.*?\)', '', df['contents'][i])
        df['contents'][i] = re.sub('[\(\[].*?[\)\]]', '', df['contents'][i])

    prompt_column = []
    completion_column = []

    num_parts = (-df['contents'].map(len).max()//-1000)

    for i in df['File name']:
        for part_num in range(num_parts):
            prompt_column.append(i.lower() + " part" + str(part_num+1))

    for j in df['contents']:
        
        split_data = j.split('.')
        avg_len = len(split_data)//num_parts + 1
        for part_num in range(num_parts - 1):
            completion_column.append('.'.join(split_data[part_num*avg_len:(part_num+1)*avg_len]))

        completion_column.append('.'.join(split_data[(num_parts - 1)*avg_len:]))

    df_cleaned = pd.DataFrame()
    df_cleaned['File name'] = prompt_column
    df_cleaned['contents'] = completion_column

            
    return df_cleaned[df_cleaned['contents'] != '']


def generate_visual_prompt(category="nature", subcategory="forest", details="tall trees with sunlight filtering through", 
                           mood="serene", color_palette="earthy tones", lighting="soft morning light", 
                           perspective="eye-level", style="realistic", action="leaves rustling in the wind"):
    prompt = f"Create a {mood} {style} image of a {subcategory} in {category}, featuring {details}. "
    prompt += f"The scene should be captured from a {perspective} perspective, using a {color_palette} color palette with {lighting}. "
    if action:
        prompt += f"Include dynamic elements like {action}. "
    prompt += "Ensure the image is visually cohesive and striking."
    return prompt

def generate_image(text="2 cute owls in a forest, Award-Winning Art, Detailed, Photorealistic, Fanart", size="1024x1024", save_img=True, use_llm_enhance=True, gen_source='replicate', image_name=None): 
    
    if gen_source == 'replicate':
        # import replicate as rp
        REPLICATE_API_TOKEN = os.environ.get('replicate_key')
        replicate = rp.Client(api_token=REPLICATE_API_TOKEN)
        prompt = generate_image_prompt(text)

        rr = replicate.run(
        "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
        input={
            "width": 768,
            "height": 768,
            "prompt": prompt,
            "scheduler": "K_EULER",
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 50
        }
        )

        # rr = replicate.run(
        # "playgroundai/playground-v2-1024px-aesthetic:42fe626e41cc811eaf02c94b892774839268ce1994ea778eba97103fe1ef51b8",
        # input={
        #     "width": 1024,
        #     "height": 1024,
        #     "prompt": prompt,
        #     "scheduler": "K_EULER_ANCESTRAL",
        #     "guidance_scale": 3,
        #     "apply_watermark": False,
        #     "negative_prompt": "",
        #     "num_inference_steps": 50
        # }
        # )

        # update to save as gif !!! create gifs from existing images
        # rr = replicate.run(
        # "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
        # input={
        #     "cond_aug": 0.02,
        #     "decoding_t": 7,
        #     "input_image": "https://replicate.delivery/pbxt/JvLi9smWKKDfQpylBYosqQRfPKZPntuAziesp0VuPjidq61n/rocket.png",
        #     "video_length": "14_frames_with_svd",
        #     "sizing_strategy": "maintain_aspect_ratio",
        #     "motion_bucket_id": 127,
        #     "frames_per_second": 6
        # }
        # )


        image_urls = rr
    else:
        openai.api_key=os.getenv("ozz_api_key")
        prompt = generate_image_prompt(text)

        res = openai.Image.create( 
            # text describing the generated image 
            prompt=prompt, 
            # number of images to generate  
            n=1, 
            # size of each generated image 
            size=size, 
            model="dall-e-3"
        ) 
        # returning the URL of one image as  
        # we are generating only one image 
        
        image_urls = [img["url"] for img in res["data"]]
       
    db_name = 'master_text_image.json'
    MT_Image_path = os.path.join(OZZ_DB, db_name)
    MT_Image = init_text_image_db(db_name)

    # Save data for each image in the database
    image_responses = {}
    for i, url in enumerate(image_urls):
        response, file_path = save_image(url, gen_source, image_name)
        image_responses[file_path] = response
        data = text_image_fields(file_path=file_path, text=prompt)
        MT_Image.append(data)
    
    save_json(MT_Image_path, MT_Image)

    return image_responses


def save_image(url1, gen_source='dalle', image_name=None):
    response = requests.get(url1) 
    if image_name:
        fname = f'{image_name}.png'
    else:
        date = str(datetime.now())
        hash_name = hash_string(date)
        # saving the image in PNG format
        fname = f'{gen_source}_{hash_name}.png'
    
    filepath = os.path.join(OZZ_db_images, fname)
    with open(filepath, "wb") as f: 
        f.write(response.content) 

    return response, fname


def generate_image_prompt(query="2 owls sleeping", enhancements=[]):
    # Default prompt
    prompt = f"Create an image of {query}."

    # Enhancement categories with real artist-inspired attributes
    enhancement_categories = {
        'realism': [
            "Emulate the meticulous realism of Chuck Close.",
            "Capture the lifelike details seen in the works of Audrey Flack.",
            "Achieve a photographic level of realism reminiscent of Roberto Bernardi."
        ],
        'impressionism': [
            "Infuse the scene with the enchanting brushstrokes characteristic of Claude Monet.",
            "Evoke the light and color techniques used by Camille Pissarro.",
            "Channel the dreamlike essence of Edgar Degas' impressionistic style."
        ],
        'surrealism': [
            "Explore the fantastical realms of Salvador Dalí through surrealistic elements.",
            "Incorporate dreamlike and bizarre elements inspired by René Magritte.",
            "Create a whimsical narrative akin to the surreal worlds crafted by Yves Tanguy."
        ],
        'abstract': [
            "Embrace non-representational forms reminiscent of Wassily Kandinsky's abstract works.",
            "Explore geometric abstraction inspired by Kazimir Malevich.",
            "Capture the essence of abstract expressionism seen in Joan Mitchell's paintings."
        ],
        'colorful': [
            "Infuse the composition with vibrant colors similar to the palettes of Wassily Kandinsky.",
            "Create a bold and colorful composition inspired by Sonia Delaunay.",
            "Explore the use of intense hues reminiscent of Fauvist master André Derain."
        ],
        'monochrome': [
            "Convey a powerful visual impact through a monochromatic palette, inspired by Franz Kline.",
            "Explore the emotional depth of black and white compositions, akin to Anselm Kiefer's works.",
            "Create a dramatic atmosphere using grayscale tones, influenced by the photography of Ansel Adams."
        ],
        'vintage': [
            "Evoke the nostalgia of vintage photography with sepia tones inspired by Dora Maar.",
            "Create a retro atmosphere inspired by the vintage aesthetics of Edward Hopper.",
            "Infuse the composition with a timeless quality reminiscent of the works of Norman Rockwell."
        ],
        'futuristic': [
            "Explore a futuristic cityscape inspired by the visionary architecture of Zaha Hadid.",
            "Capture the sleek and modern aesthetic seen in the works of Santiago Calatrava.",
            "Incorporate cutting-edge technology and design elements inspired by Syd Mead."
        ],
        'minimalism': [
            "Embrace simplicity and clean lines in the style of Donald Judd's minimalistic sculptures.",
            "Explore the use of negative space and simplicity inspired by Agnes Martin.",
            "Create a visually serene composition reminiscent of the minimalistic works of Yayoi Kusama."
        ],
        'expressionism': [
            "Infuse the composition with emotional intensity reminiscent of Egon Schiele's expressionistic portraits.",
            "Capture the bold and expressive brushstrokes inspired by Ernst Ludwig Kirchner.",
            "Explore the raw and emotive qualities of expressionism seen in the works of Chaim Soutine."
        ]
    }

    # Apply enhancements
    if enhancements:
        for category in enhancements:
            if category in enhancement_categories:
                prompt += f" {random.choice(enhancement_categories[category])},"
    # print(prompt)
    return prompt.rstrip(',') + "."

    # # Example usage:
    # query = "a cityscape"
    # enhancements = ['futuristic', 'realism', 'impressionism']

    # prompt = generate_image_prompt(query, enhancements)
    # print(prompt)



def upload_to_s3(local_file, bucket, s3_file):
    """
    Upload a file to an S3 bucket.

    :param local_file: Path to the local file you want to upload
    :param bucket: S3 bucket name
    :param s3_file: S3 key (path) where the file will be stored
    :return: True if the file was uploaded successfully, False otherwise
    """
    try:
        # Create an S3 client
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('s3_access_key'),
                          aws_secret_access_key=os.environ.get('s3_secret'))

        # Upload the file
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

        # # Example usage
        # audio_file_path = 'your_audio_file_path.mp3'
        # bucket_name = 'ozzz'
        # s3_key = 'audios/filename.mp3'

        # upload_to_s3(audio_file_path, bucket_name, s3_key)


def hoots_and_hootie_keywords(characters, self_image):
    return characters[self_image].get('split_query_by')


def hoots_and_hootie_vars(width=350, height=350, self_image="hootsAndHootie", face_recon=False, show_video=False, input_text=True, show_conversation=True, no_response_time=3, refresh_ask={}):
    refresh_ask = refreshAsk_kwargs()
    return {'width':width,
     'height':height,
     'self_image':self_image, 
     'face_recon':face_recon,
     'show_video':show_video,
     'input_text':input_text,
     'show_conversation':show_conversation,
     'no_response_time':no_response_time,
     'refresh_ask':refresh_ask}


def init_stories():

    stories = {
        "1. Adventure in Candyland": "Embark on a sweet journey through a magical land made of candy!",
        "2. Talking Animal Friends": "Join kids as they befriend animals who can talk and share amazing stories.",
        "3. Treasure Hunt in Pirate Cove": "Set sail for a thrilling adventure to find hidden pirate treasures!",
        "4. Rainbow Kingdom Quest": "Explore a vibrant kingdom filled with rainbow magic and exciting surprises.",
        "5. Dinosaur Time Travel": "Travel back in time with kids and meet friendly dinosaurs in a prehistoric world.",
        "6. Magic School Days": "Attend a school where kids learn incredible spells and charms for magical fun.",
        "7. Friendly Alien Encounter": "Make friends with a kind extraterrestrial visitor and embark on space adventures!",
        "8. Quest for the Missing Teddy": "Join kids on a mission to find their lost teddy bear in a charming adventure.",
        "9. Enchanted Forest Expedition": "Discover the wonders of an enchanted forest, meeting magical creatures along the way.",
        "10. Superhero Training Camp": "Kids attend a camp to develop superpowers and become pint-sized superheroes.",
        "11. Winter Wonderland Quest": "Explore a snowy wonderland filled with ice castles, snowmen, and winter magic.",
        "12. Panda Pajama Party": "Join a group of playful pandas for a pajama party full of giggles and games.",
        "13. Space Adventure Squad": "Become part of a space crew on a mission to explore distant planets and make new friends.",
        "14. Mermaid Lagoon Discovery": "Dive into an underwater world to meet friendly mermaids and sea creatures.",
        "15. Robot Friends in Robo-City": "Kids build robot friends and embark on exciting adventures in a futuristic city.",
        "16. Dragon Egg Quest": "Embark on a quest to find and hatch a magical dragon egg, leading to mythical adventures.",
        "17. Jungle Safari Expedition": "Join an adventurous safari through the jungle, encountering wild animals and hidden treasures.",
        "18. Circus Spectacular": "Step into the magical world of a circus with acrobats, clowns, and daring feats.",
        "19. Detective Puppies Mystery": "A group of adorable detective puppies solves mysteries and cracks cases.",
        "20. Teddy Bear Tea Party": "Host a delightful tea party with teddy bears, complete with tea, treats, and tales.",
        "21. Rainbow Unicorn Parade": "Witness a spectacular parade of rainbow-colored unicorns spreading joy and magic.",
        "22. Pumpkin Patch Harvest": "Visit a magical pumpkin patch where pumpkins come to life, ready for a harvest celebration.",
        "23. Time-Traveling Playground": "Kids discover a playground that takes them to different time periods for fun adventures.",
        "24. Cupcake Decorating Extravaganza": "Join a baking competition where kids decorate cupcakes in a whimsical world of sweets.",
        "25. Moonlight Fairy Dance": "Dance under the moonlight with friendly fairies, creating a magical and enchanting evening.",
        "26. Galactic Ice Cream Adventure": "Embark on a space journey to collect special ingredients for the ultimate galactic ice cream.",
        "27. Teddy Bear Hospital": "Kids become doctors for a day, taking care of teddy bears and other stuffed animals.",
        "28. Jungle Gym Olympics": "Compete in a friendly jungle gym competition with twists, turns, and laughter.",
        "29. Pirate Pizza Party": "Sail the high seas in search of the perfect pizza recipe for a swashbuckling pizza party.",
        "30. Underwater Ballet Extravaganza": "Dive into an underwater world where sea creatures put on a mesmerizing ballet performance.",
        "31. Circus Animal Talent Show": "Animals from the circus showcase their unique talents in a dazzling talent show.",
        "32. Teddy Bear Picnic Parade": "Join a parade of teddy bears as they march through the forest to a delightful picnic spot.",
        "33. Penguin Winter Games": "Compete in winter games with adorable penguins, featuring ice-skating and snowball fights.",
        "34. Enchanted Tea Garden": "Discover a magical tea garden where tea leaves come to life, telling stories and secrets.",
        "35. Rainbow Kite Festival": "Soar through the sky with colorful kites in a joyful and uplifting kite festival.",
        "36. Dragonfly Express Adventure": "Hop aboard the Dragonfly Express for a whimsical journey through fantasy landscapes.",
        "37. Bubblegum Bubble Bonanza": "Join a bubblegum-blowing contest with fantastic bubbles and playful challenges.",
        "38. Teddy Bear Space Odyssey": "Teddy bears embark on a space odyssey to explore new planets and make cosmic friends.",
        "39. Candy Cane Forest Expedition": "Venture into a forest made of candy canes, meeting sweet creatures along the way.",
        "40. Panda Puzzle Party": "Solve puzzles and challenges with a group of clever pandas in a bamboo-filled paradise.",
        "41. Magic Carpet Ride": "Embark on a magical journey on flying carpets, visiting enchanted lands and meeting magical beings.",
        "42. Marshmallow Castle Quest": "Kids set out on a quest to build a castle made entirely of marshmallows.",
        "43. Arctic Penguin Parade": "Join a parade of penguins in the Arctic, showcasing their unique talents and dance moves.",
        "44. Teddy Bear Spa Day": "Pamper teddy bears with a spa day, featuring bubble baths, massages, and relaxation.",
        "45. Starry Night Stargazing": "Gaze at the stars on a starry night, uncovering constellations and mythical stories.",
        "46. Pancake Pancake Party": "Host a pancake party with a twist, where pancakes come to life with personalities.",
        "47. Mooncake Festival Adventure": "Celebrate the Mooncake Festival with an adventure filled with lanterns and mooncakes.",
        "48. Robot Toy Parade": "Join a parade of lively robot toys, marching through the city in a joyful celebration.",
        "49. Teddy Bear Train Adventure": "Hop aboard the Teddy Bear Train for a scenic journey through teddy bear landscapes.",
        "50. Lullaby Lighthouse": "Visit a magical lighthouse where lullabies are created, soothing all who hear them.",
        "51. Teddy Bear Talent Show": "Teddy bears showcase their unique talents in a charming and entertaining talent show.",
        "52. Bubble Bath Beach Day": "Enjoy a day at the bubble bath beach, where waves are made of bubbles and laughter.",
        "53. Rainbow Slide Spectacle": "Slide down a rainbow slide in a whimsical playground filled with surprises.",
        "54. Teddy Bear Birthday Bash": "Celebrate a teddy bear's birthday with a grand party featuring games and surprises.",
        "55. Dragonfly Ballet Recital": "Watch dragonflies perform a delightful ballet recital in a magical garden setting.",
        "56. Penguin Pizza Party": "Host a pizza party with penguins, complete with snowball fights and sledding.",
        "57. Jellybean Jungle Safari": "Embark on a safari through a jungle where trees are made of jellybeans and lollipops.",
        "58. Teddy Bear Train Picnic": "Pack a picnic and board the Teddy Bear Train for a scenic journey through nature.",
        "59. Bubblegum Bubble Ballet": "Dance along with bubblegum bubbles in a whimsical ballet performance.",
        "60. Snowflake Symphony": "Listen to a symphony of snowflakes as they create magical music in a winter wonderland.",
        "61. Pancake Pillow Fort": "Build a pillow fort with pancakes, creating a cozy and delicious play space.",
        "62. Magic Lantern Moonlit Adventure": "Embark on a moonlit adventure with magical lanterns guiding the way.",
        "63. Teddy Bear Tea Time": "Host a tea party with teddy bears, complete with tiny cups and delightful treats.",
        "64. Cupcake Castle Quest": "Embark on a quest to build a castle made entirely of cupcakes, filled with surprises.",
        "65. Penguin Playground Parade": "Join a parade of penguins in a playful procession through a snowy playground.",
        "66. Rainbow Popsicle Party": "Celebrate with a popsicle party featuring a rainbow of flavors and frozen fun.",
        "67. Teddy Bear Space Carnival": "Teddy bears create a space carnival with rides, games, and cosmic treats.",
        "68. Butterfly Ballet Recital": "Watch butterflies perform a graceful ballet recital in a blooming flower garden.",
        "69. Ice Cream Island Adventure": "Explore an island made of ice cream, discovering delicious flavors and sweet surprises.",
        "70. Penguin Pirate Party": "Join penguins for a pirate-themed party with treasure hunts and ship adventures.",
        "71. Gumball Garden Gathering": "Visit a garden where gumballs grow on trees, creating a colorful and tasty landscape.",
        "72. Teddy Bear Treetop Tea Party": "Host a treetop tea party with teddy bears, surrounded by branches and laughter.",
        "73. Rainbow Roller Coaster Ride": "Experience the thrill of a roller coaster ride on a rainbow-colored track.",
        "74. Penguin Playground Picnic": "Enjoy a picnic with penguins in a snowy playground, filled with snowy fun.",
        "75. Marshmallow Mountain Expedition": "Embark on a mountain expedition where mountains are made of fluffy marshmallows.",
        "76. Teddy Bear Treasure Hunt": "Go on a treasure hunt with teddy bears, solving puzzles and finding hidden treasures.",
        "77. Bubblegum Bubble Bath Day": "Celebrate a day of bubblegum bubble baths, making bath time extra bubbly and fun.",
        "78. Penguin Painting Party": "Join penguins for a painting party, creating colorful masterpieces on snowy canvases.",
        "79. Jellybean Jungle Gym Adventure": "Navigate through a jungle gym made of jellybeans, swinging and sliding with joy.",
        "80. Teddy Bear Toyland Parade": "Participate in a parade through Toyland with teddy bears and playful toys.",
        "81. Rainbow Robot Rodeo": "Join a robot rodeo with robots performing tricks and stunts in a rainbow-filled arena.",
        "82. Penguin Pillow Fight": "Engage in a friendly pillow fight with penguins, creating fluffy chaos and laughter.",
        "83. Gumball Galaxy Adventure": "Embark on a space adventure in a galaxy filled with gumballs and cosmic wonders.",
        "84. Teddy Bear Train Adventure": "Embark on a train adventure with teddy bears, traveling through magical landscapes.",
        "85. Cotton Candy Cloud Castle": "Build a castle in the clouds made of cotton candy, creating a sugary and dreamy world.",
        "86. Penguin Pizza Paradise": "Visit a paradise where pizza grows on trees, creating a delicious and cheesy landscape.",
        "87. Cupcake Carousel Celebration": "Celebrate on a cupcake carousel, twirling with delightful flavors and sweet decorations.",
        "88. Teddy Bear Treehouse Tea Time": "Host a tea party in a treehouse with teddy bears, enjoying tea and treetop views.",
        "89. Rainbow Rocket Launch": "Experience the excitement of a rocket launch in a colorful and vibrant rainbow sky.",
        "90. Penguin Playground Pancake Party": "Host a pancake party with penguins in a snowy playground, flipping pancakes with glee.",
        "91. Marshmallow Moonwalk": "Take a moonwalk on marshmallow clouds, bouncing and floating in a sweet and fluffy space.",
        "92. Teddy Bear Tug-of-War Tournament": "Participate in a tug-of-war tournament with teddy bears, showcasing strength and teamwork.",
        "93. Bubblegum Bubble Beehive": "Explore a beehive made of bubblegum bubbles, meeting friendly bees and buzzing with joy.",
        "94. Penguin Painted Playground": "Join penguins in a playground painted with colorful patterns and lively designs.",
        "95. Jellybean Jumping Jamboree": "Engage in a jumping jamboree on a trampoline made of jellybeans, bouncing with delight.",
        "96. Teddy Bear Talent Showcase": "Showcase talents in a grand talent show with teddy bears, featuring acts of all kinds.",
        "97. Rainbow Roller Skating Rink": "Skate in a roller rink with rainbow-colored tracks, gliding and twirling with joy.",
        "98. Penguin Parade Party": "Celebrate with a parade of penguins, marching through the snow with festive music and dance.",
        "99. Gumball Garden Gala": "Attend a garden gala where gumballs bloom in vibrant colors, creating a festive and sweet atmosphere.",
        "100. Teddy Bear Tea Tower": "Build a tower of tea cups with teddy" 
    }

    return stories



