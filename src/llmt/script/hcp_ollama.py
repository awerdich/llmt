import os
import pandas as pd
import numpy as np
import logging
import time
from pathlib import Path

from llmt.ollamamodel import OllamaModel

#%% Directories and settings
data_root = os.environ.get('DATA')
data_dir = os.path.join(data_root, 'hcp')
experiment_name = 'hcp_predictions_ollama_20250520'
output_dir = os.path.join(data_dir, f'{experiment_name}_output')
Path(output_dir).mkdir(parents=True, exist_ok=True)

#%% Prepare the data set
dataset_name = 'hcp-traintest-250423.parquet'
df = pd.read_parquet(os.path.join(data_dir, dataset_name))
company_id_list = list(df['id'].unique())

#%% Log file
log_file = os.path.join(output_dir, f'{experiment_name}.log')
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ],
    datefmt='%Y%m%d-%H:%M'
)
logger = logging.getLogger(__name__)

#%% OpenAI experiment
model_name_list = ['llama2:7b', 'llama2:13b', 'llama2:70b']
for m, model_name in enumerate(model_name_list):
    print(f'Model {m + 1} / {len(model_name_list)}: {model_name}')
    model_name_str = model_name.replace(':', '_')
    model = OllamaModel(model=model_name)
    temperature = 0
    start_time = time.perf_counter()
    model_file_name = f'{experiment_name}_{model_name_str}.parquet'
    model_file = os.path.join(output_dir, model_file_name)
    if not Path(model_file).exists():
        results_df_list = []
        for c, company_id in enumerate(company_id_list):
            if (c + 1) % 20 == 0:
                print(f'Sending sample {c + 1} / {len(company_id_list)} for model {model_name_str}...')
                print(f'Execution time: {(time.perf_counter() - start_time) / 60:.2f} min')
                print()
            company_df = df.loc[df['id'] == company_id]
            name = company_df['name'].to_list()[0]
            description = company_df['description'].to_list()[0]
            response_mh = model.predict_mh(name=name, description=description, temperature=temperature, version=3)
            response_ip = model.predict_ip(name=name, description=description, temperature=temperature, version=1)
            response_op = model.predict_op(name=name, description=description, temperature=temperature, version=1)
            company_df = company_df.assign(**response_mh)
            company_df = company_df.assign(**response_ip)
            company_df = company_df.assign(**response_op)
            results_df_list.append(company_df)
        results_df = pd.concat(results_df_list, axis=0, ignore_index=True).\
                        assign(model=model_name_str)
        # Save the data for this model
        print(results_df.shape)
        print(f'Saving outputs to {model_file}')
        results_df.to_parquet(model_file)
    else:
        print(f'Model file {model_file} exists. Skipping...')