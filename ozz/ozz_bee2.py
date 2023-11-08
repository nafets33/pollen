import os
import sys
import re
import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import openai
from dotenv import load_dotenv
import requests
import json
import pygame  # Import the pygame library
from bs4 import BeautifulSoup
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
chess_piece_dir = os.path.join(current_dir, "..", "chess_piece")
sys.path.append(chess_piece_dir)
from king import hive_master_root, print_line_of_error

load_dotenv(os.path.join(hive_master_root(), '.env'))


#PlAY.HT WEBSITE APU LINK
url = "https://play.ht/api/v2/tts"
#Alpaca API keys  
# api_key_id_of_alpaca = "AKY1SU4Z08UI76AYIED3"
# api_secret_key_alpaca = "T5kSnVlCaOhG1O7Mq2N2u9tNS2983LkxCSMlOvdv"
api_secret_key_alpaca = os.environ.get("APCA_API_KEY_ID_PAPER")
api_key_id_of_alpaca = os.environ.get("APCA_API_SECRET_KEY_PAPER")
#alpaca API_URL
api_url = "https://data.alpaca.markets/v1beta1/news"
# List of target symbols_for alpaca news 
target_symbols = ["SPY", "GOOG", "TSLA", "META"]




def clean_text_for_alpaca_news(raw_text):
    # Remove non-ASCII characters and special symbols
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', raw_text)
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned_text)
    
    # Remove extra spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def alpaca_news_fetching():
    # Construct headers with API keys
    headers = {
        "Apca-Api-Key-Id": api_key_id_of_alpaca,
        "Apca-Api-Secret-Key": api_secret_key_alpaca
    }

    # Construct query parameters
    query_params = {
        "symbols": ",".join(target_symbols)
    }

    # Make the API request
    response = requests.get(api_url, headers=headers, params=query_params)
    news_data = response.json()
    first_100_words=''
    for news_item in news_data["news"]:
        symbols = ", ".join(news_item["symbols"])
        print("Symbol(s):", symbols)
        print("Headline:", news_item["headline"])

        news_url = news_item["url"]
        news_response = requests.get(news_url)
        news_html = news_response.text

        soup = BeautifulSoup(news_html, 'html.parser')

        news_text = soup.get_text()
        cleaned_news_text = clean_text_for_alpaca_news(news_text)
        first_100_words = ' '.join(cleaned_news_text.split()[:100])


        #print(f"{symbols} News :")
        #print(first_100_words)
        #print("=" * 30)
        #print("\n\n\n")
    
    return first_100_words


### NOT USED ###
class EmbeddingUtility:
    def __init__(self, embedding_model="text-embedding-ada-002"):
        self.embedding_model = embedding_model
        openai.api_key = os.environ.get('ozz_api_key')

    def get_embedding(self, text):
        text = text.replace("/n", " ")
        return openai.Embedding.create(input=[text], model=self.embedding_model)['data'][0]['embedding']

    def get_doc_embedding(self, text):
        return self.get_embedding(text)


class DocumentProcessor:
    MAX_SECTION_LEN = 1024
    SEPARATOR = "/n* "

    def __init__(self, api_params, utility: EmbeddingUtility):
        self.COMPLETIONS_API_PARAMS = api_params
        self.utility = utility

    def compute_matching_df_embeddings(self, matching_df):
        return {
            idx: self.utility.get_doc_embedding(r.description.replace("/n", " ")) for idx, r in matching_df.iterrows()
        }

    @staticmethod
    def vector_similarity(x, y):
        return np.dot(np.array(x), np.array(y))

    def order_document_sections_by_query_similarity(self, query, contexts):
        query_embedding = self.utility.get_embedding(query)
        document_similarities = sorted([
            (self.vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
        ], reverse=True)
        return document_similarities

    def construct_prompt(self, question, context_embeddings, df):
        most_relevant_document_sections = self.order_document_sections_by_query_similarity(question, context_embeddings)
        chosen_sections = []
        chosen_sections_len = 0

        for _, section_index in most_relevant_document_sections:
            document_section = df.loc[section_index]
            chosen_sections_len += len(document_section.description) + 3
            if chosen_sections_len > self.MAX_SECTION_LEN:
                break
            chosen_sections.append(self.SEPARATOR + document_section.description.replace("/n", " "))

        header = """Answer the question as truthfully as possible only using the provided context. and if the answer is not contained within the text below, say "I don't know" /n/nContext:/n"""
        return header + "".join(chosen_sections) + "/n/n Q: " + question + "/n A:"

    def answer_query_with_context(self, query, df, context_embeddings, show_prompt=False):
        prompt = self.construct_prompt(query, context_embeddings, df)
        if show_prompt:
            print(prompt)
        response = openai.Completion.create(prompt=prompt, **self.COMPLETIONS_API_PARAMS)
        return response["choices"][0]["text"].strip(" /n")


def preprocessing(df):
    for i in df.index:
        desc = df.loc[i, 'description']
        if isinstance(desc, str):
            df.loc[i, 'description'] = desc.replace('/n', '')
            df.loc[i, 'description'] = re.sub(r'/(.*?/)', '', df.loc[i, 'description'])
            df.loc[i, 'description'] = re.sub('[/(/[].*?[/)/]]', '', df.loc[i, 'description'])
    return df


def closest_sentiment_match(dfs, query_sentiment):
    closest_index = None
    closest_difference = float('inf')
    analyzer = SentimentIntensityAnalyzer()

    for index, sub_df in enumerate(dfs):
        titles = sub_df['description'].tolist()
        aggregated_sentiment = 0

        for title in titles:
            aggregated_sentiment += analyzer.polarity_scores(title)['compound']

        average_sentiment = aggregated_sentiment / len(titles)
        difference = abs(average_sentiment - query_sentiment)

        if difference < closest_difference:
            closest_difference = difference
            closest_index = index
    return closest_index

# function for voice generation using the api of play.ht
def voice_generate(prompt):
    payload = {
    "text": prompt,
    "voice": "Stella",
    "quality": "medium",
    "output_format": "mp3",
    "speed": 0.8,
    "sample_rate": 24000
    }
    headers = {
        "accept": "text/event-stream",
        "content-type": "application/json",
        "AUTHORIZATION": "e3e4dff721f1423591b9572252608b9d",
        "X-USER-ID": "ZUOemZt5dpV8bs90zg9C4o1zrMu1"
    }

    response = requests.post(url, json=payload, headers=headers)

    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')

            if decoded_line.startswith("data:"):
                try:
                    event_data = json.loads(decoded_line[6:])
                    if event_data.get("stage") == "complete":
                        audio_url = event_data.get("url")
                        #print("Voice response generated successfully!")
                        #print("Audio URL:", audio_url)

                        # Download the generated audio file
                        audio_response = requests.get(audio_url)
                        audio_file = "output.mp3"
                        with open(audio_file, "wb") as f:
                            f.write(audio_response.content)

                        # Initialize pygame
                        pygame.init()
                        pygame.mixer.init()

                        # Load and play the audio file
                        pygame.mixer.music.load(audio_file)
                        pygame.mixer.music.play()

                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)

                        pygame.mixer.quit()

                        break
                except json.JSONDecodeError:
                    pass
### NOT USED ###





# here we call the news function of aplaca by passing query in the function
def main():
    #filename = "D:/Viral Square/Stephen_ozz/pollen/pollen/ozz/fake_job_postings.csv"
    #df = pd.read_csv(filename, engine='python', on_bad_lines='skip')
    #df.dropna(subset=['title', 'location'], inplace=True)
    #df.drop_duplicates(inplace=True)
    df = pd.DataFrame({'description': [alpaca_news_fetching()]})
    ## for ever ticker return its seintment score
    def symbol_sientiment_score(ticker, news_text, min=-8, max=8):
        score = 0
        return score


    # df = preprocessing(df)
    #dfs_25 = [df.iloc[i:i+25] for i in range(0, len(df), 25)]
    # dfs_25 = [df]

    # all_articles = []

    # analyzer = SentimentIntensityAnalyzer()
    # query = alpaca_news_fetching()  

    # query_sentiment = analyzer.polarity_scores(query)['compound']
    # matched_index = closest_sentiment_match(dfs_25, query_sentiment)
    
    # # print("The closest matching index in dfs_25 is:", matched_index)
    # # print(dfs_25[matched_index])
    # # print(df.columns)

    # utility = EmbeddingUtility()
    # doc_processor = DocumentProcessor({
    #     "temperature": 0.0,
    #     "max_tokens": 300,
    #     "model": "text-davinci-003",
    # }, utility)

    # # print(dfs_25[matched_index])
    # query = 'what is the latest news regarding TSLA'
    # # Replace the DataFrame at matched_index with a new DataFrame containing the query
    # dfs_25[matched_index] = pd.DataFrame({'description': [query]})
    # matching_df_embeddings = doc_processor.compute_matching_df_embeddings(dfs_25[matched_index])

    # resp = doc_processor.answer_query_with_context(query, dfs_25[matched_index], matching_df_embeddings)
    
    # print(f"\n\n\nYour query is: {query}\n")
    # print(resp)
    # voice_generate(resp)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        print_line_of_error()





# What kind of jobs are available for teachers abroad?
# What is the monthly salary for jobs in Asia for teachers?
# What qualifications are required for the English Teacher Abroad position?
# What responsibilities does the RMA Coordinator have in the Customer Success team?
# What are the preferred qualifications for the Junior Python Developer position?
# What are the values that Upstream believes in as mentioned in the job description?
# What are the main responsibilities of the Customer Service Associate at Novitex Enterprise Solutions?
# What are the key requirements for the Data Entry Clerk II position?
# What are the job responsibilities of an Engagement Executive at Upstream?
# How many years of work experience are required for the Engagement Executive position?