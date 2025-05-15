""" Run HCP experiment 01. """

import os
import time
import pandas as pd
from pathlib import Path
import logging

from llmt.openaimodel import OpenAIModel

#%% Directories and settings
n_runs = 10 # Repeat the experiment
temperature_list = [0.0, 0.7]
experiment_name = 'hcp_experiment_03'
# data_root = os.path.join(os.environ.get('HOME'), 'data')
data_root = os.path.join(os.environ.get('HOME'), 'home_data')
data_dir = os.path.join(data_root, 'hcp')
output_dir = os.path.join(data_dir, experiment_name)
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Mapping true variable and predictions
variable_dict = {'mental_health': 'pred_mh',
                 'inpatient': 'pred_ip',
                 'outpatient': 'pred_op'}

# The data file
data_file = os.path.join(data_dir, 'hcp-alldata-250413.parquet')
df_all_samples = pd.read_parquet(data_file)
df_train = df_all_samples.loc[df_all_samples['dset'] == 'train'].\
    reset_index(drop=True).\
    astype({var: int for var in variable_dict.keys()})

#%% The test samples (new samples to create predictions)
n_test_samples = 0
random_state = 42

df_test = df_all_samples.\
    loc[df_all_samples['mental_health'].isnull()].\
    sample(n_test_samples, random_state=random_state, replace=False).\
    reset_index(drop=True)

df = pd.concat([df_train, df_test], axis=0, ignore_index=True).\
    sample(frac=1, random_state=random_state).\
    reset_index(drop=True)

for dset in ['train', 'test']:
    print(f'Number of {dset.upper()} samples: {df[df["dset"] == dset].shape[0]}')

company_id_list = list(df['id'].unique())
print(f'Number of unique companies: {len(company_id_list)}')

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

#%% Set up the experiment
model = OpenAIModel(model='gpt-4o')
start_time = time.perf_counter()

for t, temperature in enumerate(temperature_list):
    logger.info(f'Experiment {t+1}/{len(temperature_list)}: temperature = {temperature}')
    for run in range(n_runs):
        execution_time_min = (time.perf_counter() - start_time) / 60
        print(f'Execution time: {execution_time_min:.2f} min')
        print(f'Run {run+1}/{n_runs}: temperature = {temperature}')
        logger.info(f'Run {run+1}/{n_runs}')
        results_run_file_name = f'250423_mh3ip1op1_{str(run+1).zfill(2)}_t{t+1}.parquet'
        results_run_df_list = []
        for c, company_id in enumerate(company_id_list):
            if (c+1) % 20 == 0:
                print(f'Sample {c+1}/{len(company_id_list)}')
            company_df = df.loc[df['id'] == company_id]
            name = company_df['name'].values[0]
            description = company_df['description'].values[0]
            response_mh = model.predict_mh(name=name, description=description, version=3, temperature=temperature)
            response_ip = model.predict_ip(name=name, description=description, version=1, temperature=temperature)
            response_op = model.predict_op(name=name, description=description, version=1, temperature=temperature)
            company_df = company_df.assign(**response_mh)
            company_df = company_df.assign(**response_ip)
            company_df = company_df.assign(**response_op)
            results_run_df_list.append(company_df)
        results_run_df = pd.concat(results_run_df_list, axis=0, ignore_index=True)
        results_run_df = results_run_df.assign(temperature=temperature, run=run+1)
        results_run_df.to_parquet(os.path.join(output_dir, results_run_file_name))