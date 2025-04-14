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
        success = dotenv.load_dotenv()
        if success:
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.api_endpoint = os.getenv('OPENAI_API_ENDPOINT')
            self.api_version = os.getenv('OPENAI_API_VERSION')
            self.api_project = os.getenv('OPENAI_API_PROJECT')
        else:
            logger.error('Error: Failed to load .env file')

    def create_client(self):
        api_dict = {'api_version': self.api_version,
                    'azure_endpoint': self.api_endpoint,
                    'api_key': self.api_key}
        return AzureOpenAI(**api_dict)

