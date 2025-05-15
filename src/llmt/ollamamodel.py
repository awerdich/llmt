""" Create an Ollama client and send messages to a local model """

import logging
from tqdm import tqdm
from ollama import Client
from llmt.llmtools import process_prompt, Prompt

# OpenAI functions
from llmt.openai import MentalHealth, InpatientServices, OutpatientServices, create_messages

logger = logging.getLogger(__name__)

def response_message(response):
    output = None
    if response.get('done', None):
        if response.get('done_reason', None) == 'stop':
            output = response.message.content
            # clean up the response message
            output = output.\
                replace('\n', '').\
                replace('\t', '').\
                replace(' ','')
    return output

class Ollama:
    def __init__(self, host: str = 'ollama', port: int = 11434):
        self.host = host
        self.port = port
        self.models = self.list_models()

    def create_client(self):
        client = None
        url = f'http://{self.host}:{self.port}'
        try:
            client = Client(host=url)
        except Exception as e:
            logger.error(f'Error creating client: {e}')
        return client

    def list_models(self):
        client = self.create_client()
        model_list = None
        try:
            model_list = client.list().get('models', None)
            model_list = [model.get('model', None) for model in model_list]
        except Exception as e:
            logger.error(f'Error retrieving model list: {e}')
        return model_list

    def pull_model(self, model_name: str) -> bool:
        """
        Pull (download) a model from the Ollama server with a progress bar.
        Args:
            model_name (str): Name of the model to pull
        Returns:
            bool: True if successful, False otherwise
        """
        client = self.create_client()
        if not client:
            logger.error(f'Failed to create client connection')
            return False
        try:
            # Start pulling the model and listen to progress
            with tqdm(unit='B', unit_scale=True, desc=model_name, dynamic_ncols=True) as pbar:
                for progress in client.pull(model_name, stream=True):
                    # Each progress update is a dictionary
                    if 'total' in progress and 'completed' in progress:
                        pbar.total = progress['total']
                        pbar.update(progress['completed'] - pbar.n)
                    elif 'status' in progress:
                        # Optionally print status updates
                        pbar.set_postfix_str(progress['status'])

            logger.info(f'Successfully pulled model: {model_name}')
            return True
        except Exception as e:
            logger.error(f'Failed to pull model {model_name}: {e}')
            return False

    def send_messages(self,
                      messages: list,
                      model: str,
                      response_format,
                      temperature: float = 0.7,
                      client = None):
        if client is None:
            client = self.create_client()
        try:
            response = client.chat(model=model,
                                   messages=messages,
                                   format=response_format.model_json_schema(),
                                   options={'temperature': temperature})
            message = response_message(response)
            output = response_format.model_validate_json(message)
            output = output.model_dump()
        except Exception as e:
            logger.error(f'Error sending messages: {e}')
            output = None
        else:
            response_dump = response.model_dump()
            output.update({'done': response_dump.get('done', None),
                           'done_reason': response_dump.get('done_reason', None)})
        return output


class OllamaModel(Ollama):
    def __init__(self, model: str = 'llama2:7b'):
        super().__init__()
        self.model = model
        self.client = self.create_client()

    def predict_mh(self, name, description, version, temperature=0):
        variable = 'mental_health'
        pred_col = 'pred_mh'
        mh_prompt_name = f'{variable}_system_{str(version).zfill(2)}'
        system_prompt = Prompt().load(prompt_name=mh_prompt_name)
        user_prompt = process_prompt(f"""
                        The organization {name} is described as: {description} 
                        Does this organization provide {variable} healthcare services?
                        """)
        messages = create_messages(system_prompt=system_prompt, user_prompt=user_prompt)
        output = self.send_messages(messages=messages,
                                    model=self.model,
                                    temperature=temperature,
                                    response_format=MentalHealth,
                                    client=self.client)
        output.update({pred_col: 1 if output.get(pred_col) == True else 0})
        output = {pred_col: output.get(pred_col)}
        return output