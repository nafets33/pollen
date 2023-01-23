import openai_secret_manager
import openai

def train_model(content, model_engine, api_key):
    # Get the API key from the openai_secret_manager
    secrets = openai_secret_manager.get_secrets(api_key)
    openai.api_key = secrets["api_key"]
    
    # Prepare the content for training
    if isinstance(content, str):
        content = content.encode() # if the content is string, convert it to bytes
    elif isinstance(content, bytes):
        pass
    else:
        raise ValueError("Invalid content type. Only str and bytes are accepted.")
    
    # Use the `openai.Completion.create()` function to train the model on the content
    response = openai.Completion.create(
        engine=model_engine,
        prompt=(content),
        max_tokens=4096,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response

# script 2
import openai

def generate_response(prompt, model_engine, api_key):
    # Get the API key from the openai_secret_manager
    secrets = openai_secret_manager.get_secrets(api_key)
    openai.api_key = secrets["api_key"]
    
    # Use the `openai.Completion.create()` function to send the prompt to the model and get a response
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=4096,
        n=1,
        stop=None,
        temperature=0.5
    )
    return response

# score text generation
# However, you can use metrics like BLEU, METEOR, ROUGE, CIDEr etc to evaluate the quality of generated text.
# They are widely used to evaluate the quality of machine-generated text against the reference text.
# You can use these metrics to compare the generated text with the reference text and get a score, but keep in mind that these metrics are not perfect, and the scores they provide are not always reliable indicators of text quality.