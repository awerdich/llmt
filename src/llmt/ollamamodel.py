""" Create an Ollama client and send messages to a local model """

import logging
from tqdm import tqdm
from ollama import Client
from llmt.llmtools import process_prompt, Prompt

# Pydantic models
from llmt.llmtools import MentalHealth, InpatientServices, OutpatientServices, create_messages

logger = logging.getLogger(__name__)

def response2message(response):
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
        output = False
        if not client:
            logger.error(f'Failed to create client connection')
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
            output = True
            self.models = self.list_models()  # Update the model list after pulling the model
        except Exception as e:
            logger.error(f'Failed to pull model {model_name}: {e}')
        return output

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
            message = response2message(response)
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
        self.client = self.create_client()
        self.model = model
        if model not in self.models:
            logger.warning(f'Model {model} not found in the Ollama server. '
                           f'Trying to pull the model from the server...')
            self.pull_model(model)
            if model not in self.models:
                logger.error(f'Failed to pull model {model} from the server. '
                             f'Please check the model name and try again.')
                exit(1)

    def predict_mh(self, name, description, version, temperature=0):
        response_format = MentalHealth
        pred_var = 'pred_mh'
        messages = Prompt().create_mh_messages(name=name, description=description, version=version)
        output = self.send_messages(messages=messages,
                                    model=self.model,
                                    temperature=temperature,
                                    response_format=response_format,
                                    client=self.client)
        output.update({pred_var: 1 if output.get(pred_var) == True else 0})
        output = {pred_var: output.get(pred_var)}
        return output

    def predict_ip(self, name, description, version, temperature=0):
        response_format = InpatientServices
        pred_var = 'pred_ip'
        messages = Prompt().create_ip_messages(name=name, description=description, version=version)
        output = self.send_messages(messages=messages,
                                    model=self.model,
                                    temperature=temperature,
                                    response_format=response_format,
                                    client=self.client)
        output.update({pred_var: 1 if output.get(pred_var) == True else 0})
        output = {pred_var: output.get(pred_var)}
        return output

    def predict_op(self, name, description, version, temperature=0):
        pred_var = 'pred_op'
        verified_var = 'verified_op'
        output_var_list = [pred_var, verified_var]
        messages = Prompt().create_op_messages(name=name, description=description, version=version)
        output = self.send_messages(messages=messages,
                                    model=self.model,
                                    temperature=temperature,
                                    response_format=OutpatientServices,
                                    client=self.client)
        output.update({key: 1 if output.get(key) == True else 0 for key in output_var_list})
        output = {var: output.get(var) for var in output_var_list if output.get(var) is not None}
        return output