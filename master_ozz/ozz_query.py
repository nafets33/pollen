import json
import os
import openai
from dotenv import load_dotenv
import shutil
import string
import pandas as pd
from datetime import datetime
import pytz
import re
import copy
# from collections import deque

os.umask(0o000)
est = pytz.timezone("US/Eastern")
pg_migration = os.getenv("pg_migration")

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from master_ozz.utils import llm_assistant_response, get_last_eight, ozz_characters, init_stories ,hoots_and_hootie_vars, common_phrases_for_Questions, save_json, load_local_json, init_text_audio_db, print_line_of_error, ozz_master_root, ozz_master_root_db, generate_audio, save_audio, Retriever, init_constants
from chess_piece.queen_hive import init_clientUser_dbroot
from chess_piece.pollen_db import PollenDatabase

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSIST_PATH')
OZZ_BUILD_dir = constants.get('OZZ_BUILD_dir')
# OZZ_db_audio = constants.get('OZZ_db_audio')
# OZZ_db_images = constants.get('OZZ_db_images')
characters = ozz_characters()
root_db = ozz_master_root_db()


def clean_response(response):
    # Remove asterisks specifically, but keep other punctuation like ? and !
    cleaned_response = re.sub(r'\*', '', response)
    
    # Replace multiple spaces with a single space
    cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
    
    # Strip leading and trailing whitespace
    cleaned_response = cleaned_response.strip()
    
    return cleaned_response


def remove_exact_string(string_a, string_b):
    # Split string_a by string_b
    split_strings = string_a.split(string_b)
    
    # Join the split strings without the occurrences of string_b
    final_string_a = ''.join(split_strings)

    return final_string_a

def split_string(current_query, last_response):
    if last_response:
        # Find the index of the last occurrence of the ending of b in a
        index = current_query.rfind(last_response[-8:])
        
        # Check if the ending of b is found in a
        if index != -1:
            # Split a at the index of the ending of b
            return current_query[index + len(last_response[-8:]):].strip()
        else:
            # If the ending is not found, return the original string a
            return current_query.strip()
    else:
        return current_query.strip()

    # Example usage:
    string_b = "i'm good thanks for asking" # llm
    string_a = "good thanks for asking hi" # user query

    result = split_string(string_a, string_b)
    print("Result:", result)


def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)
# Setting up the llm for conversation with conversation history

def copy_and_replace_rename(source_path, destination_directory, build_file_name='temp_audio'):
    try:
        # Extract the file name and extension
        file_name, file_extension = os.path.splitext(os.path.basename(source_path))

        # Construct the new file name (e.g., 'xyz.txt')
        new_file_name = build_file_name + file_extension

        # Construct the full destination path
        destination_path = os.path.join(destination_directory, new_file_name)

        # Copy the file from source to destination, overwriting if it exists
        shutil.copy2(source_path, destination_path)
        
        # print(f"File copied from {source_path} to {destination_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {source_path}")

    except PermissionError:
        print(f"Error: Permission denied while copying to {destination_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def process_response(response):
    # Convert the response to lowercase
    response_lower = response.lower()

    # Remove special characters, including question marks
    response_cleaned = ''.join(char for char in response_lower if char.isalnum() or char.isspace())

    # # Example usage
    # input_response = "What's are you doing?"
    # processed_response = process_response(input_response)
    # print(processed_response)
    return response_cleaned


def calculate_similarity(response1, response2):
    # Create a CountVectorizer to convert responses to vectors
    vectorizer = CountVectorizer().fit_transform([response1, response2])

    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(vectorizer)

    # Extract the cosine similarity score
    similarity_score = similarity_matrix[0, 1]

    # # Example usage
    # response1 = "What are you doing?"
    # response2 = "What are you"

    # similarity_score = calculate_similarity(response1, response2)
    # print(f"Cosine Similarity: {similarity_score}")
    return similarity_score


# are we asking LLM to find answer in db or reteriver?
def determine_embedding(current_query, use_embedding=None):
    s = datetime.now()
    # print("EMBEDDINGS")
    if use_embedding:
        db_name=use_embedding
        print("embedding", db_name)
        return db_name, current_query
    db_name=None
    # our_embeddings_phrases = ["where's", 'do you have', 'suggest', 'what kind', 'tell me', 'help', 'store', 'how much', 'where is', 'looking for', 'hoot couture', 'hoot couture kids', 'something about the store', 'in the store', 'clothes do you have', 'do you have']
    # for phrase in our_embeddings_phrases:
    #     if phrase in current_query:
    #         print("EMBEDDING FOUND: phrase>> ", phrase)
    #         our_embeddings = True
    #         db_name = 'monroe_center'
            # if phrase == 'mayor' or 'say hi':
            #     if 'mayor' in current_query:
            #         current_query = current_query + "say hi to the mayor and use his full name if you can find it, offer him a cup of tea, and wish him the best of luck with his duties taking care of hoboken, also the best of luck in the upcoming election"
            #         db_name = 'db_mayor_demo'


    print("embedding", db_name)
    # print('detemine embedding:', (datetime.now() - s).total_seconds())
    return db_name, current_query


def handle_prompt(self_image, conversation_history, main_prompt=None, characters=characters, system_info=False):
    try:
        
        self_image_name = self_image.split('.')[0]
        
        if not main_prompt:
            main_prompt = characters[self_image_name].get('main_prompt')
        
        if len(conversation_history) == 0: # FIRST ASK
            conversation_history.append({"role": "system", "content": main_prompt})
        
        if system_info:
            main_prompt = conversation_history[0].get('content')
            conversation_history[0] = {"role": "system", "content": main_prompt + system_info}

        return conversation_history
    except Exception as e:
        print_line_of_error(e)


def story_time_params():
    return True

def client_user_session_state_return(text, response_type='response', returning_question=False, current_youtube_search=False, max_results=10, story_time={}, hh_vars={}, use_embeddings=[], session_listen=False, command=False,):
    hh_vars = hh_vars if hh_vars else hoots_and_hootie_vars()

    return {'text': text, # []
            'response_type': response_type,
            'returning_question': returning_question,
            'current_youtube_search': current_youtube_search,
            'max_results': max_results,
            'story_time': story_time,
            'hh_vars': hh_vars,
            'use_embeddings': use_embeddings,
            'session_listen': session_listen,
            'command': command,
            }


def search_for_something(current_query):
    search_phrases = ['search', 'find me', 'look for', 'find a', 'looking for']
    for s_phrase in search_phrases:
        if s_phrase in current_query:
            return s_phrase
    
    return False


def calculate_story(current_query):
    def join_string_columns_optimized(df, col_name='title'):
    # Use apply along with str.cat to join string columns
        df['title'] = df.apply(lambda x: x[x.apply(lambda y: isinstance(y, str))].astype(str).str.cat(sep=' '), axis=1)

        return df

    stories = init_stories()
    query = "tell me more a story about dinasours"
    dfs_25 = pd.DataFrame(stories.items())
    dfs_25=join_string_columns_optimized(dfs_25)
    # analyzer = SentimentIntensityAnalyzer()
    # query_sentiment = analyzer.polarity_scores(query)['compound']
    # matched_index = closest_sentiment_match([dfs_25], query_sentiment)
    winner = None
    for story in dfs_25['title']:
        if calculate_similarity(story, current_query) > .95:
            winner = story

def determine_command(current_query):
    lower_query = current_query.lower()
    # command_types = {'create confluence':'create confluence', 'edit confluence':'edit confluence', 'save sharepoint':'save sharepoint', 'create email':'create email', 'save session':'save session'}
    # for commandkey, command in command_types.items():
    if 'create' in lower_query and 'confluence' in lower_query:
        return 'create_confluence'

    return False

def handle_commands(command, session_state):
    if command == 'create_confluence':
        if session_state.get('page_title'):
            pass
        else:
            return "You Need a Title"
    
    return True

def ai_create_name_for_session(master_conversation_history):
    # 
    return True

### MAIN 
def Scenarios(text: list, current_query: str , conversation_history: list , master_conversation_history: list, session_state={}, audio_file=None, self_image='hootsAndHootie.png', client_user=None, use_embeddings=None, df_master_audio=None, check_for_story=False):
    scenario_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    OZZ = {}
    s3_filepath = f'{client_user}/'

    def scenario_return(response, conversation_history, audio_file, session_state, self_image=None):
        return {'response': response,
                'conversation_history': conversation_history,
                'audio_file': audio_file,
                'session_state': session_state,
                'self_image': self_image,}

    def find_audio(response, master_text_audio, audio_file = False):
        # if response in audio db or 95% in audio db, return audio file
        s = datetime.now()

        df = pd.DataFrame(master_text_audio)
        audio_text = dict(zip(df['file_path'], df['text'])) # audio, text
        if master_text_audio:
            # response = process_response(response)
            for db_audio_file, ozz_reponse in audio_text.items():
                # ozz_reponse = process_response(ozz_reponse)
                if calculate_similarity(response, ozz_reponse) > .95:
                    # print("audio found")
                    return db_audio_file
        print('findaudio:', (datetime.now() - s).total_seconds())

        return audio_file

    def handle_audio(user_query, response, audio_file=None, self_image=None, s3_filepath=None):
        s = datetime.now()
        
        db_name, master_text_audio = init_text_audio_db()
        df = pd.DataFrame(master_text_audio)
        audio_text = dict(zip(df['file_path'], df['text'])) # audio, text
        fnames = len(audio_text)
        db_DB_audio = os.path.join(root_db, 'audio')



        # check is response already in audio db per character WORKERBEE
        if not audio_file:
            audio_file = find_audio(response, master_text_audio)

        if audio_file: # if
            print("AUDIO FOUND ", audio_file)
            # source_file = os.path.join(db_DB_audio, audio_file)
            # destination_directory = OZZ_BUILD_dir
            # copy_and_replace_rename(source_file, destination_directory)

            return audio_file
        else:
            ## NEW AUDIO
            fname_image = self_image.split('.')[0]
            voice_id = characters[fname_image].get('voice_id')
            settings_vars={'stability': .71, 'similarity_boost': .5, 'style': 0.0}
            if fname_image == 'viki':
                print('VIKI audio')
                settings_vars={'stability': .5, 'similarity_boost': .8, 'style': 0.0}

            filename = f'{fname_image}__{fnames}.mp3'
            audio_file = filename #os.path.join(db_DB_audio, filename)
            print("NEW AUDIO", audio_file)
            model_id = 'eleven_monolingual_v1' # if len(response) < 300 else 'eleven_turbo_v2'

            audio = generate_audio(query=response, voice_id=voice_id, model_id=model_id, settings_vars=settings_vars)
            print('audiofunc generate:', (datetime.now() - s).total_seconds())

            if audio:
                s3_filepath = s3_filepath + filename
                local_path = save_audio(filename, audio, response, user_query, self_image, db_name, s3_filepath)
                # clean up and delete file WORKERBEE
                os.chmod(local_path, 0o666)
                # filename, audio, response, user_query, self_image=False, db_name='master_text_audio.json', s3_filepath=None
                print('audiofunc Saved:', (datetime.now() - s).total_seconds())
            else:
                audio_file = "techincal_errors.mp3"
                # source_file = os.path.join(db_DB_audio, audio_file)
                # destination_directory = OZZ_BUILD_dir
                # copy_and_replace_rename(source_file, destination_directory)

        print('audiofunc:', (datetime.now() - s).total_seconds())

        return audio_file

    def story_response(current_query, session_state, returning_question=False):
        try:
            s = datetime.now()
            response=None
            audio_file=None
            
            story_asks = ["tell a story", "share a tale", "share a tail", "story please", "tell me a story", "tell the kids a story", "tell the story"]
            story_db = {'calendar_story_1.mp3': ['calendar story'],
                        'owl_story_1.mp3': ['owl story'],}
            tell_phrases = ['tell me', 'tell the', 'please tell']
            for k, v in story_db.items():
                for tag in v:
                    for tell_phrase in tell_phrases:
                        sa = f'{tell_phrase} {tag}' 
                        story_asks.append(sa)
            
            if returning_question:
                for audio_file, story_tags in story_db.items():
                    find_story = [i for i in story_tags if i in ask]
                    if find_story:
                        response = "story_time"
                        audio_file = audio_file
                    #     break
                    # else:
                    #     print("Could not Find Story")
                    #     response = "What Story would you like to hear?"
                    #     session_state['response_type'] = 'question' 
            
            story_ask = [ask for ask in story_asks if ask in current_query]
            print(story_ask)
            for ask in story_asks:
                if ask in current_query:
                    print("ask in query ", ask)
                    story_ask = [ask]

            if story_ask:
                ask = story_ask[0]
                for audio_file, story_tags in story_db.items():
                    find_story = [i for i in story_tags if i in ask]
                    if find_story:
                        print("STORY FOUND")
                        response = "story_time"
                        audio_file = audio_file
                        break
                    # else:
                    #     print("Could not Find Story")
                    #     response = "What Story would you like to hear?"
                    #     session_state['response_type'] = 'question'
                    #     audio_file = None
            # print('queryfunc:', (datetime.now() - s).total_seconds())
            return {'response': response, 'audio_file': audio_file, 'session_state': session_state}
        except Exception as e:
            print_line_of_error(e)
            return None
    
    def youtube_response(current_query, session_state, returning_question=False):
        if 'search for videos' in current_query:
            print("youtube trigger")

    def search_for(search_phrase, current_query, session_state, returning_question=False):
        # search for what?
        if 'story' in current_query:
            print("tell a story")
        if "video" in current_query:
            print("search for a video")
            youtube_query = f'{current_query} SYSTEM NOTE: reword this query in the best way for a youtube video search'
            search_video_phrase = llm_assistant_response(youtube_query, [])
            session_state['current_youtube_search'] = search_video_phrase
        
        return current_query, session_state

    def handle_code_blocks(response):
        return response

    print('QUERY ', current_query)
    # print('SSTATE ', {i: v for i, v in session_state.items() if i != 'text'})
    
    user_query = current_query

    # WATERFALL OF QUERY RESPONSE
    ## checks (limit)
    ## check commands

    # Scenario Limit
    df_mch = pd.DataFrame(conversation_history)

    if len(df_mch) > 0:
        if 'client_user' in df_mch.columns:
            df_mch['datetime'] = pd.to_datetime(df_mch['datetime'], format="%Y-%m-%d %H-%M-%S %p %Z", errors='coerce')
            today = datetime.now(est).replace(hour=0)
            df_mch = df_mch[df_mch['datetime'] > today]
            cl_user_questions = len(df_mch[df_mch['client_user'] == client_user])
            print('stop len', cl_user_questions)
            if cl_user_questions > 15 and client_user != 'stefanstapinski@gmail.com':
                # return good bye message 
                response = "Hey sorry but you've reached the max number of questions to ask. Talking to me literally costs money...time is money after all even with computers. Maybe next time we can speak for real. "
                # Appending the response from json file
                conversation_history.append({"role": "assistant", "content": response})
                
                # return audio file
                audio_file = 'stefan_max_conv_len.mp3' # handle_audio(user_query, response, audio_file=audio_file, self_image=self_image)

                text[-1].update({'resp': response})
                session_state['text'] = text
                master_conversation_history.append({"role": "assistant", "content": response, "self_image": self_image, 'datetime': return_timestamp_string()})
                session_state['returning_question'] = False
                session_state['response_type'] = 'response'
                listen_after_reply = session_state['returning_question']

                return scenario_return(response, conversation_history, audio_file, session_state, self_image)
        
            if cl_user_questions == 5:
                system_info = " Please tell the user that they have 5 more questions remaining before you need to leave"
                conversation_history = handle_prompt(self_image, conversation_history, system_info=system_info)

    command = determine_command(current_query)
    if command != False:
        print("COMMAND FOUND ", command)

    # check for command or ongoing command
    # if session_state.get('command'):
        # have we satisfied command? If so move on to execution
        # if session_state.get('command_')

    # Appending the user question from json file
    search_phrase = search_for_something(current_query)
    if search_phrase:
        current_query, session_state = search_for(search_phrase, current_query, session_state)
    else:
        session_state['current_youtube_search'] = False

    ### WATER FALL RESPONSE ###
    # check_for_story
    if check_for_story:
        resp_func = story_response(current_query, session_state)
        if resp_func.get('response'):
            print("func response found")
            response = resp_func.get('response')
            audio_file = resp_func.get('audio_file')
            session_state = resp_func.get('session_state')
            conversation_history.append({"role": "assistant", "content": response, })
            audio_file = handle_audio(user_query, response, audio_file, self_image, s3_filepath)
            return scenario_return(response, conversation_history, audio_file, session_state, self_image)

    # Common Phrases # WORKERBEE Add check against audio_text DB
    # print("common phrases")
    s = datetime.now()
    # for query, response in common_phrases.items():
    #     if query.lower() == current_query.lower():
    #         print("QUERY already found in db: ", query)

    #         # Appending the response from json file
    #         conversation_history.append({"role": "assistant", "content": response})
    #         ## find audio file to set to new_audio False
    #         # return audio file
    #         audio_file = handle_audio(user_query, response, audio_file=audio_file, self_image=self_image, s3_filepath=s3_filepath) 
    #         print('common phrases:', (datetime.now() - s).total_seconds())
    #         # self_image = 'hoots_waves.gif'
    #         return scenario_return(response, conversation_history, audio_file, session_state, self_image)

    # if len(df_master_audio) == 1:
    #     response = df_master_audio.iloc[-1].get('text')
    #     # Appending the response from json file
    #     conversation_history.append({"role": "assistant", "content": response})
    #     ## find audio file to set to new_audio False
    #     # return audio file
    #     audio_file = handle_audio(user_query, response, audio_file=audio_file, self_image=self_image) 
    #     print('common phrases:', (datetime.now() - s).total_seconds())
    #     # self_image = 'hoots_waves.gif'
    #     return scenario_return(response, conversation_history, audio_file, session_state, self_image)


    # LLM
    print("LLM")
    # try: ## force not responding with a question
    #     assistant = [v['content'] for v in conversation_history if v['role'] == 'assistant']
    #     questions=0
    #     if len(assistant) > 0:
    #         for as_resp in assistant:
    #             if "?" in as_resp:
    #                 questions+=1
    #     do_not_reply_as_a_question = True if questions > 1 else False
    #     print("do_not_reply_as_a_question", do_not_reply_as_a_question)

    #     if do_not_reply_as_a_question:
    #         current_query = "do not respond with a question"  + current_query
   
    # except Exception as e:
    #     print_line_of_error(e)

    handle_questions = f"If you are not asking a question do not put any question mark symbols in the response. If you are asking a question make sure the question mark symbol is exactly at the end of the text: "
    
    use_embedding = use_embeddings[0] if use_embeddings else None
    db_name, current_query = determine_embedding(current_query, use_embedding=use_embedding)
    return_only_text=True
    llm_convHistory = copy.deepcopy(conversation_history)
    if db_name:
        print("USE EMBEDDINGS: ", db_name)
        Retriever_db = os.path.join(PERSIST_PATH, db_name)
        response = Retriever(current_query, Retriever_db, return_only_text=return_only_text)
        if return_only_text:
            source_documents = [i.page_content for i in response]
            current_query = current_query + f""". Use the following information below to try and answer the above query. 
            If the informaiton is not relevant to the above query then do not lie and ask the user if they could be more specific in their ask. 
            {handle_questions}

            Below is source context:
            {source_documents}
            """
            llm_convHistory.append({"role": "user", "content": current_query})
            response = llm_assistant_response(llm_convHistory)
        else:
            response = response.get('result')

    else:
        print("CALL LLM - GPT")
        current_query =  handle_questions + current_query
        llm_convHistory.append({"role": "user", "content": current_query})
        response = llm_assistant_response(llm_convHistory)
    
    
    conversation_history.append({"role": "assistant", "content": response})
    audio_file = handle_audio(user_query, response=response, audio_file=audio_file, self_image=self_image, s3_filepath=s3_filepath)

    if 'viki' in self_image:
        copy_conversation_history = copy.deepcopy(conversation_history)
        copy_conversation_history = []
        copy_conversation_history.append({"role": "user", "content": f"take this below text and return it translated into Russian {response}"})
        russ_response = llm_assistant_response(copy_conversation_history)
        conversation_history.pop()
        conversation_history.append({"role": "assistant", "content": f'{response} -TRANSLATED- {russ_response}'})
        response = f'{response} -TRANSLATED- {russ_response}'

    return scenario_return(response, conversation_history, audio_file, session_state, self_image)

def ozz_query(text, self_image, refresh_ask, client_user, force_db_root=False, page_direct=False, listen_after_reply=False, session_listen=False, before_trigger_vars={}):
    
    def ozz_query_json_return(text, self_image, audio_file, page_direct, listen_after_reply=False, session_state=None):
        json_data = {'text': text, 
                    'audio_path': audio_file, 
                    'self_image': self_image, 
                    'page_direct': page_direct, 
                    'listen_after_reply': listen_after_reply,
                    'session_state': session_state,}
        return json_data
    
    def clean_current_query_from_previous_ai_response(text, split_query_by=['stefan', 'stephen', 'stephanie', 'stephan']):
        # take previous ai response and remove if it found in current_query
        # if 'assistant' in last_text:
        current_query = text[-1]['user'] # user query
        if len(text) > 1:
            ai_last_resp = text[-2]['resp']
        else:
            ai_last_resp = None
        
        if ai_last_resp:
            current_query = split_string(current_query=current_query, last_response=ai_last_resp)

        # WORKERBEE confirm is senitentment of phrase is outside bounds of responding to
        lower_query = current_query.lower() 
        for kword in split_query_by:
            if kword in lower_query:
                current_query = lower_query.split(kword)[1]
                break

        # reset user with cleaned reponse
        text[-1]['user'] = current_query

        return text, current_query

    def story_time(current_query: str, text: list, self_image:str, audio_file:str, page_direct:bool, listen_after_reply: bool, session_state: dict):
        page_number = session_state.get('page_number')


        if page_number == 0: # Story Time INIT
            story_ideas = {}

    
    
        return ozz_query_json_return(text, self_image, audio_file, page_direct, listen_after_reply)

    db_root = init_clientUser_dbroot(client_username=client_user, force_db_root=force_db_root)

    # handle character from self_image
    # handle command type, if you don't know command type you need to ask?
    # if 'this is a command' in current_query or "please do this": ## handle command requests:
    #     if "save this" in current_query:
    #         save_json()
    self_image_name = self_image.split('.')[0]
    split_query_by = characters[self_image_name].get('split_query_by')
    text, current_query = clean_current_query_from_previous_ai_response(text, split_query_by)
    print(current_query)
    if len(current_query) <= 1:
        print("NO RESPONSE RETURN BLANK")
        # return ozz_query_json_return(text, self_image, audio_file=None, page_direct=None, listen_after_reply=False)
        current_query = "hello"
    
    first_ask = True if len(text) <= 1 else False

    common_phrases_ = common_phrases_for_Questions()

    ## Load Client session and conv history # based on character
    if pg_migration:
        master_conversation_history = PollenDatabase.retrieve_data(db_root, '-MASTER_CONVERSATIONAL_HISTORY')
        conversation_history = PollenDatabase.retrieve_data(db_root, '-CONVERSATIONAL_HISTORY')
        session_state = PollenDatabase.retrieve_data(db_root, 'SESSION_STATE')
        master_conversation_history_file_path = None
        conversation_history_file_path = None
        session_state_file_path = None
    else:
        master_conversation_history_file_path = os.path.join(db_root, 'master_conversation_history.json')
        conversation_history_file_path = os.path.join(db_root, 'conversation_history.json')
        session_state_file_path = os.path.join(db_root, 'session_state.json')
    
        # load db
        master_conversation_history = load_local_json(master_conversation_history_file_path)
        conversation_history = load_local_json(conversation_history_file_path)
    
        # Session State
        session_state = load_local_json(session_state_file_path)
    
    session_state['session_listen'] = session_listen
    if 'viki' in self_image:
        use_embeddings = False
    else:
        use_embeddings=session_state.get('use_embeddings')

    # handle prompt 1 and ensure light conv history
    conversation_history = handle_prompt(self_image, conversation_history, main_prompt=True, characters=characters, system_info=refresh_ask.get('header_prompt'))
    conversation_history = get_last_eight(conversation_history)

    # # If query was already ASKED find audio and don't call LLM # WORKERBEE
    self_image_name = self_image.split('.')[0]
    # master_text_audio_name, master_text_audio = init_text_audio_db()
    # df_master_audio = pd.DataFrame(master_text_audio)
    # if len(df_master_audio) > 0:
    #     df_master_audio = df_master_audio[(df_master_audio['self_image']==self_image_name) & (df_master_audio['text']==current_query)]

    print("USE EMBED", use_embeddings)
    if first_ask:
        system_info = " this is your first interaction, be polite and ask them a question on what they want to talk about, work, physics, basketball, AI, investments, family, fun. "
        conversation_history = handle_prompt(self_image, conversation_history, system_info=system_info)

        conversation_history =  conversation_history.clear() if len(conversation_history) > 0 else conversation_history
        conversation_history = [] if not conversation_history else conversation_history
        conversation_history = handle_prompt(self_image, conversation_history)
        conversation_history.append({"role": "user", "content": current_query})
        session_state = client_user_session_state_return(text, response_type='response', returning_question=False, use_embeddings=use_embeddings)
    else:
        system_info = " this is not your first interaction, be more percise with answers, don't ask how there days is going or other introduction questions "
        conversation_history = handle_prompt(self_image, conversation_history, system_info=system_info)
        session_state = session_state
        conversation_history.append({"role": "user", "content": current_query})

    storytime = True if session_state['story_time'] else False

    # Call the Scenario Function and get the response accordingly
    scenario_resp = Scenarios(text, current_query, conversation_history, master_conversation_history, session_state, self_image=self_image, client_user=client_user, use_embeddings=use_embeddings, df_master_audio=None) # df_master_audio
    response = scenario_resp.get('response')
    response = clean_response(response)

    # print("RESPONSE", response)
    conversation_history = scenario_resp.get('conversation_history')
    audio_file = scenario_resp.get('audio_file')
    session_state = scenario_resp.get('session_state')
    self_image = scenario_resp.get('self_image')

    # Save Data
    # def save_response(text, current_query, response, client_user, self_image, session_state, master_conversation_history)
    session_listen = session_state.get('session_listen')
    master_conversation_history.append({"role": "user", "content": current_query, 'client_user': client_user, 'datetime': return_timestamp_string(), 'session': session_listen, })
    master_conversation_history.append({"role": "assistant", "content": response, "self_image": self_image, 'datetime': return_timestamp_string(), 'session': session_listen})
    text[-1].update({'resp': response})
    session_state['text'] = text
    
    # # Question Return?
    # if response.endswith("?"):
    #     session_state['returning_question'] = True
    #     session_state['response_type'] = 'question'
    # else:
    #     session_state['returning_question'] = False
    #     session_state['response_type'] = 'response'
    # listen_after_reply = session_state['returning_question'] # True if session_state.get('response_type') == 'question' else False
    listen_after_reply=False

    page_direct= False # if redirect, add redirect page into session_state
    if not session_state['current_youtube_search']:
        pass
    else:
        page_direct="http://localhost:8501/"

    # For saving a chat history for current session in json file
    save_json(master_conversation_history_file_path, master_conversation_history)
    save_json(conversation_history_file_path, conversation_history)
    save_json(session_state_file_path, session_state)

    print("listen after reply", listen_after_reply)
    print("AUDIOFILE:", audio_file)
    print("IMAGE:", self_image)
    
    return ozz_query_json_return(text, self_image, audio_file, page_direct, listen_after_reply)

## db 

## def save_interaction(client_user, what_said, date, ai_respone, ai_image) # fact table

## def embedd_the_day()

## short term memory vs long term memory
