import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import ozz_characters, hoots_and_hootie_keywords, ozz_master_root, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants, refreshAsk_kwargs
# from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
import requests
import base64
import ipdb
from pq_auth import signin_main

# from custom_button import cust_Button
load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####

CONSTANTS = init_constants()

def hoots_and_hootie(width=350, height=350, 
                     self_image="jamescfp.png", 
                     face_recon=True, 
                     show_video=False, 
                     input_text=True, 
                     show_conversation=True, 
                     no_response_time=3,
                     refresh_ask={},
                     use_embeddings=[],
                     before_trigger={},
                     phrases=[],
                     agent_actions=["Research", "Rebalance Portfolio", 
                                    "Financial Planning", "Risk Assessment", 
                                    ]
                     ):
    
    to_builder = VoiceGPT_options_builder.create()
    to = to_builder.build()

    force_db_root = True if 'force_db_root' in st.session_state and st.session_state['force_db_root'] else False

    custom_voiceGPT(
        api=f"{st.session_state['ip_address']}/api/data/voiceGPT",
        api_key=os.environ.get('ozz_key'),
        client_user=st.session_state['client_user'],
        self_image=self_image,
        width=width,
        height=height,
        hello_audio=None, # "test_audio.mp3",
        face_recon=face_recon, # True False, if face for 4 seconds, trigger api unless text being recorded trigger api, else pass
        show_video=show_video, # True False, show the video on page
        # listen=listen, # True False if True go into listen mode to trigger api
        input_text=input_text,
        show_conversation=show_conversation,
        no_response_time=no_response_time,
        refresh_ask=refresh_ask,
        force_db_root=force_db_root,
        before_trigger={'how are you': 'hoots_waves__272.mp3', 'phrases': phrases},
        api_audio=f"{st.session_state['ip_address']}/api/data/local/",
        # use_embeddings=use_embeddings,
        commands=[{
            "keywords": phrases, # keywords are case insensitive
            "api_body": {"keyword": "hey hoots"},
        }, {
            "keywords": ["bye Hoots"],
            "api_body": {"keyword": "bye hoots"},
        }
        ],
        agent_actions=agent_actions,
        key=st.session_state.get('self_image', 'jamescfp'),
        datatree={},
        datatree_title="",
    )

    return True

def ozz(user_auth=False):

    client_user = st.session_state['client_user']
    db_root = st.session_state['db_root']
    session_state_file_path = os.path.join(db_root, 'session_state.json')
    prod = st.session_state['prod']

    cols = st.columns((3,2))
    with cols[0]:
        col_1 = st.empty()
    # with cols[1]:
    with st.sidebar:
        col_2 = st.empty()

    characters = ozz_characters()
    st.session_state['characters'] = characters
    # user_session_state = init_user_session_state(prod, db_root)

    with col_2.container():
        self_image = st.selectbox("Speak To", options=['jamescfp'], key='self_image')
    st.write(self_image)
    header_prompt = characters[st.session_state.get('self_image')].get('main_prompt')

    # with tabs[1]:
    if st.sidebar.toggle("Edit System Prompt", key='edit_system_prompt'):
        header_prompt = st.text_area("System_Prompt", header_prompt, height=500)
        if st.button("save main prompt"):
            st.info("DB Not Setup Yet")

    refresh_ask = refreshAsk_kwargs(prod, user_auth=user_auth, header_prompt=header_prompt)
    width= 350 #st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
    height= 350 # st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
    self_image= f"{st.session_state.get('self_image')}.png" # st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else f"{st.session_state.get('self_image')}.png"
    face_recon= False #st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
    show_video= False # st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
    input_text= True # st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
    show_conversation= True # st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
    no_response_time= 3 # st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 3

    no_response_time = st.sidebar.slider('No Response Time', max_value=8, value=no_response_time)

    embedding_default = []
    if self_image == 'stefan.png':
        with col_1.container():
            st.header(f"Stefans '''~Conscience'''...")
            text = "...Well sort of, it's WIP...Responses may be delay'd, ⚡faster-thinking and processing always costs more 💰"
            st.write(text)

        embedding_default = ['stefan']
    # elif self_image == 'jamescfp.png':
    #     with col_1.container():
    #         st.header(f"James Your Portfolio Manager")

        embedding_default = ['jamescfp']

    else:
        embedding_default = []
        # user_session_state['use_embeddings'] = embedding_default
        # save_json(session_state_file_path, user_session_state)

    with st.sidebar:
        embeddings = os.listdir(CONSTANTS.get('PERSIST_PATH'))
        embeddings = ['None'] + embeddings
        if [i for i in embedding_default if i not in embeddings]:
            embedding_default = ['None']
        
        use_embeddings = st.multiselect("use embeddings", default=embedding_default, options=embeddings)
        st.session_state['use_embedding'] = use_embeddings
        if st.button("save"):
            # user_session_state['use_embeddings'] = use_embeddings
            # save_json(session_state_file_path, user_session_state)
            st.info("saved")
    

    with st.sidebar:
        # rep_output = st.empty()
        selected_audio_file=st.empty()
        llm_audio=st.empty()


    phrases = hoots_and_hootie_keywords(characters, self_image.split(".")[0])

    # with tabs[0]:
    hoots_and_hootie(
        width=width,
        height=height,
        self_image=self_image,
        face_recon=face_recon,
        show_video=show_video,
        input_text=input_text,
        show_conversation=show_conversation,
        no_response_time=no_response_time,
        refresh_ask=refresh_ask,
        use_embeddings=use_embeddings,
        phrases=phrases,
        )


    def local_gif(gif_path, width="33", height="33", sidebar=False, url=False):
        if url:
            data_url = data_url
        else:
            with open(gif_path, "rb") as file_:
                contents = file_.read()
                data_url = base64.b64encode(contents).decode("utf-8")
            if sidebar:
                st.sidebar.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                    unsafe_allow_html=True,
                )

        return True


    # st.write(client_user)
    if client_user == 'stefanstapinski@gmail.com':
        with st.sidebar:
            st.write("Admin Only")
if __name__ == '__main__':
    signin_main()
    user_auth = True if 'authentication_status' in st.session_state and st.session_state['authentication_status'] else False
    ozz(user_auth)

