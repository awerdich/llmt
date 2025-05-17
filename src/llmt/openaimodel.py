""" Create OpenAI client and send messages to the API """

import os
import logging
import dotenv
from openai import AzureOpenAI
from llmt.llmtools import process_prompt, Prompt
from llmt.llmtools import MentalHealth, InpatientServices, OutpatientServices, create_messages

logger = logging.getLogger(__name__)

class OpenAI:
    def __init__(self):
        env = dotenv.load_dotenv()
        if env:
            self.api_access = {'api_version': os.getenv('OPENAI_API_VERSION'),
                               'azure_endpoint': os.getenv('OPENAI_API_ENDPOINT'),
                               'api_key': os.getenv('OPENAI_API_KEY')}
        else:
            logger.error('Error: Failed to load .env file')

    def create_client(self):
        client = None
        try:
            client = AzureOpenAI(**self.api_access,)
        except Exception as e:
            logger.error(f'Error: {e}')
        return client

    def send_messages(self,
                      messages: list,
                      model: str,
                      response_format,
                      temperature: float = 0.7,
                      client = None):
        if client is None:
            client = self.create_client()
        try:
            response = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format=response_format)
            output = response.choices[0].message.parsed.model_dump()
        except Exception as e:
            logger.error(f'Error: {e}')
            output = None
        else:
            response_dump = response.choices[0].model_dump()
            output.update({'refusal': response_dump.get('refusal', None)})
        return output

class OpenAIModel(OpenAI):
    def __init__(self, model: str = 'gpt-4o'):
        super().__init__()
        self.model = model
        self.client = self.create_client()

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
