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

    def predict_ip(self, name, description, version, temperature=0):
        variable = 'inpatient'
        pred_col = 'pred_ip'
        ip_prompt_name = f'{variable}_system_{str(version).zfill(2)}'
        system_prompt = Prompt().load(prompt_name=ip_prompt_name)
        user_prompt = process_prompt(f"""
                        The organization {name} is described as: {description} 
                        Does this organization provide {variable} healthcare services?
                        """)
        messages = create_messages(system_prompt=system_prompt, user_prompt=user_prompt)
        output = self.send_messages(messages=messages,
                                    model=self.model,
                                    temperature=temperature,
                                    response_format=InpatientServices,
                                    client=self.client)
        output.update({pred_col: 1 if output.get(pred_col) == True else 0})
        output = {pred_col: output.get(pred_col)}
        return output

    def predict_op(self, name, description, version, temperature=0):
        variable = 'outpatient'
        pred_col = 'pred_op'
        op_prompt_name = f'{variable}_system_{str(version).zfill(2)}'
        system_prompt = Prompt().load(prompt_name=op_prompt_name)
        user_prompt = process_prompt(f"""
                        The organization {name} is described as: {description} 
                        Does this organization provide {variable} healthcare services?
                        """)
        messages = create_messages(system_prompt=system_prompt, user_prompt=user_prompt)
        output = self.send_messages(messages=messages,
                                    model=self.model,
                                    temperature=temperature,
                                    response_format=OutpatientServices,
                                    client=self.client)
        key_list = [pred_col, 'verified_op']
        output.update({key: 1 if output.get(key) == True else 0 for key in key_list})
        output = {pred_col: output.get(pred_col), 'verified_op': output.get('verified_op')}
        return output
