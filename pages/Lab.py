import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import llm_assistant_response, ozz_characters,handle_prompt, get_last_eight, load_local_json, ozz_master_root, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
# from ozz_auth import all_page_auth_signin
from pq_auth import signin_main
 
from dotenv import load_dotenv


main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

def lab():
    
    ip_address = st.session_state['ip_address']
    client_user = st.session_state['client_user']

    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')

    def delete_files_in_directory(directory):
        try:
            # List all files in the directory
            files = os.listdir(directory)
            
            # Iterate over each file and delete it
            for file in files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
            
            print("All files deleted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    with st.sidebar:
        if st.button("Clear DATA files"):
            delete_files_in_directory(DATA_PATH)

    with st.sidebar:
    # with ozz_lab_lab:
        files = st.sidebar.file_uploader('Upload your files',type=['PDF','CSV','MD','DOCX','DOC','XLSX','PY','HTML', 'TXT'],accept_multiple_files=True)
        
        # Store all the files
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)

        # Iterating over files and saving it 
        for file in files:
            if file is not None:
                with open(os.path.join(DATA_PATH, file.name), 'wb') as f:
                    f.write(file.read())
                # st.write(f"Saved {file.name}")

        # Training the files or creating embeddings and storing in vector dbs

        # Predefined options for the select box
        predefined_options = os.listdir(PERSIST_PATH)

        # Text input for custom value
        custom_value = st.text_input("Add New DB Name")
        if custom_value not in predefined_options:
            predefined_options.append(custom_value)

        # Select box with predefined options
        db_name = st.selectbox("Train DB", predefined_options)
        chunk_size = st.number_input('chunk size', min_value=100, max_value=800, value=500)
        chunk_overlap = st.number_input('chunk overlap', min_value=10, max_value=100, value=20)
        if files is not None:
            if st.sidebar.button('Train'):
                with st.sidebar.status("Training Model..."):
                    load_files = Directory(DATA_PATH)
                    # clean data WORKERBEE
                    # load_files = clean_data(data)
                    chunks = CreateChunks(load_files, chunk_size, chunk_overlap)
                    embeddings = CreateEmbeddings(chunks, os.path.join(PERSIST_PATH, db_name))
                    st.info(f"EMBEDDING Created {db_name}")


    # Show all the uploaded files
    file_names = [name for name in os.listdir(DATA_PATH) if os.path.isfile(os.path.join(DATA_PATH, name))]
    if not file_names:
        st.write('You have no files uploaded.')
    else:
        selected_file = st.sidebar.selectbox(label="Uploaded Files", options=file_names)
    return_only_text = True if st.toggle("text query only", True) else False

    db_root = st.session_state['db_root']
    score_threshold = st.number_input("score_threshold", min_value=0.0, max_value=1.0,value=.6)
    search_kwards_num = st.number_input("search_kwards_num", min_value=1, max_value=33,value=8)

    ## Load Client session and conv history # based on character
    master_conversation_history_file_path = os.path.join(db_root, 'master_conversation_history.json')
    conversation_history_file_path = os.path.join(db_root, 'conversation_history.json')
    session_state_file_path = os.path.join(db_root, 'session_state.json')
    
    # load db
    conversation_history = load_local_json(conversation_history_file_path)

    # master_conversation_history = load_local_json(master_conversation_history_file_path)
    conversation_history = get_last_eight(conversation_history, num_items=4)

    characters = ozz_characters()

    first_ask = True if 'refresh_count' in st.session_state and st.session_state['refresh_count'] > 0 else False
    if first_ask:
        system_info = " this is your first interaction, be polite and ask them a question on what they want to talk about, work, physics, basketball, AI, investments, family, fun. "
        conversation_history =  conversation_history.clear() if len(conversation_history) > 0 else conversation_history

    st.session_state['refresh_count'] = 1

    # Chat Interface
    db_names = os.listdir(PERSIST_PATH)
    db_name = st.selectbox("Chat with DB: ", db_names, index=db_names.index('stefan'))
    query = st.chat_input(placeholder="Enter your query")
    import ipdb
    if query is not None:
        with st.chat_message('user'):
            st.write(query)

        # Exception or error handling of response
        try:
            llm_result ={}
            if query:
                source_documents={}
                with st.spinner("Searching..."):
                    Retriever_db = os.path.join(PERSIST_PATH, db_name)
                    if return_only_text:
                        r_response = Retriever(query, Retriever_db, search_kwards_num=search_kwards_num, score_threshold=score_threshold, return_only_text=return_only_text )
                        source_documents = [i.page_content for i in source_documents]
                        print(source_documents)
                        # Handle Prompt
                        conversation_history = handle_prompt(characters, "stefan", conversation_history)
                        st.write(conversation_history)
                        current_query = query + f""". Use the following information below to try and answer the above query. 
                        If the informaiton is not relevant to the above query then do not lie and ask the user if they could be more specific in their ask. 
                        {source_documents}
                        """
                        conversation_history.append({"role": "user", "content": current_query})
                        llm_response = llm_assistant_response(conversation_history)
                        llm_result['llm_result'] = llm_response

            # if return_only_text == False:
            with st.chat_message('ai'):
                response = Retriever(query, Retriever_db, search_kwards_num=4, score_threshold=score_threshold, return_only_text=False)
                query = response.get("query")
                result = response.get("result")
                llm_result = llm_result.get('llm_result')
                st.write("LLM: ", llm_result)
                ret_source_documents = response.get("source_documents")
                st.write(ret_source_documents)
                
                st.write("RETRIEVER ", result)
                st.markdown("###### Here are top 3 search results",unsafe_allow_html=True)
                for index, document in enumerate(r_response):
                    with st.status(f"Document {index+1}"):
                        page_content = document.page_content
                        formatted_content = ' '.join(line.strip() for line in page_content.split('\n'))
                        metadata = document.metadata
                        if 'page' in metadata:
                            st.markdown(f""" > Content: <br><hr>
                                        {formatted_content} <br><hr>
                                        Source Document: {metadata['source']} \n
                                        Page Number: {metadata['page']+1}""",unsafe_allow_html=True)
                        elif 'row' in metadata:
                            st.markdown(f""" > Content: <br><hr>
                                        {formatted_content} <br><hr>
                                        Source Document: {metadata['source']} \n
                                        Row Number: {metadata['row']+1}""",unsafe_allow_html=True)
                        else:
                            st.markdown(f""" > Content: <br><hr>
                                        {formatted_content} <br><hr>
                                        Source Document: {metadata['source']} \n""",unsafe_allow_html=True)
        except Exception as e:
            with st.chat_message('ai'):
                st.write('There are some problems with your docs or something went wrong :(')
                print_line_of_error(e)
if __name__ == '__main__':
    auth_ = signin_main()
    lab()