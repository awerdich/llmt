import os
import glob
import logging
from pathlib import Path
from textwrap import dedent
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

def process_prompt(prompt: str):
    output = dedent(prompt).replace('\n', '').strip()
    return output

class MentalHealth(BaseModel):
    predict_mh: bool = Field(description='A business that provides mental health or behavioral healthcare '
                                         'services for human patients.')
    predict_mh_score: float = Field(description='Confidence that the business provides mental '
                                                'health or behavioral healthcare services (0-1).')

class Prompt:
    def __init__(self, prompt_dir: str = None, prompt_file_ext: str = '.md'):
        if prompt_dir is None:
            prompt_dir = os.path.join(Path(__file__).parent, 'prompt')
        self.prompt_dir = prompt_dir
        self.prompt_file_ext = prompt_file_ext

    def list(self):
        file_list = glob.glob(os.path.join(self.prompt_dir,
                                           f'*{self.prompt_file_ext}'))
        prompt_name_list = [os.path.splitext(os.path.basename(file))[0] for file in file_list]
        return prompt_name_list

    def load(self, prompt_name: str):
        prompt_file = os.path.join(self.prompt_dir, f'{prompt_name}{self.prompt_file_ext}')
        output = None
        try:
            with open(prompt_file, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
                output = process_prompt(markdown_content)
        except FileNotFoundError:
            logger.error(f'Error: File not found at "{prompt_file}"')
        except Exception as e:
            logger.error(f'An error occurred: {e}')
        return output
