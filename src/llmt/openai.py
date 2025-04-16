import os
import logging
import dotenv
from openai import AzureOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

def create_messages(system_prompt: str, user_prompt: str):
    system_message = {'role': 'system', 'content': system_prompt}
    user_message = {'role': 'user', 'content': user_prompt}
    message_list = [system_message, user_message]
    return message_list

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
                      temperature: float = 0.7,
                      response_format = None,
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
