""" Training set predictions for HCP training data 07/01/2025 """
import os
import copy
import numpy as np
import pandas as pd
import time
import logging
from pandas.core.frame import DataFrame

from llmt.openaimodel import OpenAIModel
from llmt.performance import Performance

#%% Paths and files
data_dir = os.path.join(os.environ.get('DATA'), 'hcp')
data_file_name = 'hcp-train-250701.parquet'
df = pd.read_parquet(os.path.join(data_dir, data_file_name))
company_id_list = list(df['id'].unique())
print(f'Number of unique companies: {len(company_id_list)}')

#%% Variables and parameters
col_dict = {'mental_health': 'pred_mh',
            'inpatient': 'pred_ip',
            'outpatient': 'pred_op'}
stat_col_dict = copy.deepcopy(col_dict)
stat_col_dict.update({'mental_health_inpatient': 'pred_mh_ip',
                      'mental_health_outpatient': 'pred_mh_op'})
true_col_list = list(col_dict.keys())
pred_col_list = [col_dict.get(k) for k in true_col_list]
deployment_name_list = ['gpt-4o-1120', 'gpt-4.1']
version_dict_list = [{'mh': 3, 'ip': 1, 'op': 1}, {'mh': 4, 'ip': 2, 'op': 2}]
output_base_name = 'hcp-train-250701'

#%% Log file
log_file = os.path.join(data_dir, f'{output_base_name}.log')
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

#%% Support functions
# Run the prediction functions for a specific model
def predict_classes(model, name: str, description: str, temperature: float=0, version_dict: dict=None) -> list:
    if version_dict is None:
        version_dict = {'mh': 3, 'ip': 1, 'op': 1}
    response_list = []
    response_mh = model.predict_mh(name=name,
                                   description=description,
                                   temperature=temperature,
                                   version=version_dict.get('mh'))
    response_list.append(response_mh)
    response_ip = model.predict_ip(name=name,
                                   description=description,
                                   temperature=temperature,
                                   version=version_dict.get('ip'))
    response_list.append(response_ip)
    response_op = model.predict_op(name=name,
                                   description=description,
                                   temperature=temperature,
                                   version=version_dict.get('op'))
    response_list.append(response_op)
    assert len(response_list) == 3
    return response_list

# Function to send a sample to the model
def send_sample(cdf: DataFrame, deployment: str, version_dict: dict) -> DataFrame:
    assert len(cdf) == 1, 'The input data frame is one sample and should have just ONE ROW!'
    company_n = cdf.get('name').values[0]
    company_d = cdf.get('description').values[0]
    model = OpenAIModel(model=deployment)
    response_list = predict_classes(model=model,
                                    name=company_n,
                                    description=company_d,
                                    temperature=0,
                                    version_dict=version_dict)
    # Add the responses to the company_df dataframe
    for response in response_list:
        cdf = cdf.assign(**response)
    # Combine the binary columns
    cdf = Performance(data=cdf). \
        combine_columns(true_col_list=['mental_health', 'inpatient'],
                        pred_col_list=['pred_mh', 'pred_ip']). \
        rename(columns={'pred_mh_pred_ip': 'pred_mh_ip'})

    cdf = Performance(data=cdf). \
        combine_columns(true_col_list=['mental_health', 'outpatient'],
                        pred_col_list=['pred_mh', 'pred_op']). \
        rename(columns={'pred_mh_pred_op': 'pred_mh_op'})

    return cdf

def performance_table(data: DataFrame, true_pred_cols: dict = None) -> DataFrame:
    if true_pred_cols is None:
        true_pred_cols = {'mental_health': 'pred_mh',
                          'inpatient': 'pred_ip',
                          'outpatient': 'pred_op'}
    performance_df_list = []
    for v, (true_col, pred_col) in enumerate(true_pred_cols.items()):
        performance_dict = Performance(data=data).binary_performance(true_col=true_col, pred_col=pred_col)
        performance_df = pd.DataFrame(performance_dict, index=[v])
        performance_df.insert(loc=0, column='category', value=true_col)
        performance_df_list.append(performance_df)
    performance_df = pd.concat(performance_df_list, axis=0)
    return performance_df


def save_output(data: DataFrame, file_base: str, file_dir: str) -> bool:
    """ Save a data frame as .parquet and .csv files """
    file_base_name = os.path.basename(os.path.splitext(file_base)[0])
    assert os.path.exists(file_dir), f'output directory {file_dir} does not exist!'
    parquet_file = os.path.join(file_dir, f'{file_base_name}.parquet')
    csv_file = os.path.join(file_dir, f'{file_base_name}.csv')
    success = False
    try:
        data.to_parquet(parquet_file)
        data.to_csv(csv_file, index=False)
    except Exception as e:
        logger.error(f'ERROR saving output files: {e}')
    else:
        assert os.path.exists(parquet_file), f'Parquet file {parquet_file} not found.'
        assert os.path.exists(csv_file), f'CSV file {csv_file} not found.'
        success = True
    return success

#%% Run the predictions for the training data with performance evaluation
start_time = time.perf_counter()
results_samples_df_list = []
results_stat_df_list = []
for d, deployment_name in enumerate(deployment_name_list):
    print(f'Model  {d+1}/{len(deployment_name_list)}: {deployment_name}')
    for p, prompt_version_dict in enumerate(version_dict_list):
        print(f'Prompt {p + 1}/{len(version_dict_list)}: {prompt_version_dict}')
        results_samples_list = []
        for c, company_id in enumerate(company_id_list[:6]):
            if (c + 1) % 2 == 0:
                print(f'Sample {c + 1}/{len(company_id_list)}')
            company_df = df.loc[df['id'] == company_id]
            company_name = company_df.get('name').values[0]
            company_desc = company_df.get('description').values[0]
            result_df = send_sample(cdf=company_df,
                                    deployment=deployment_name,
                                    version_dict=prompt_version_dict)
            results_samples_list.append(result_df)
        # Assemble the results for this model/prompt combination
        results_samples = pd.concat(results_samples_list, axis=0, ignore_index=True)
        results_stat = performance_table(data=results_samples, true_pred_cols=stat_col_dict)
        # Add some descriptions for the model and prompt to the tables
        results_samples.insert(loc=0, column='model', value=deployment_name)
        results_samples.insert(loc=1, column='prompt', value=p + 1)
        results_stat.insert(loc=0, column='model', value=deployment_name)
        results_stat.insert(loc=1, column='prompt', value=p + 1)
        # Save the table in a list before we run the next prompt/model combination
        results_samples_df_list.append(results_samples)
        results_stat_df_list.append(results_stat)
results_samples_df = pd.concat(results_samples_df_list, axis=0, ignore_index=True)
results_stat_df = pd.concat(results_stat_df_list, axis=0, ignore_index=True)
# Save the data as .parquet and .csv files
save_output(data=results_samples_df, file_base=f'{output_base_name}-samples', file_dir=data_dir)
save_output(data=results_stat_df, file_base=f'{output_base_name}-performance', file_dir=data_dir)