""" File operations including downloading and extracting archives """

import os
import glob
import pandas as pd
import numpy as np
import shutil
import traceback
import contextlib
import gzip
from urllib import request
from urllib.error import HTTPError
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class DownloadProgressBar(tqdm):
    """ Small helper class to make a download bar """

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class FileOP:

    def __init__(self, data_output_dir=None):
        self.data_output_dir = data_output_dir
        self.url = None

    def unzip(self, in_file, out_file):
        """
        Unzip .gz file and return file size
        :param in_file: complete file path of compressed .gz file
        :param out_file: complete file path of output file
        :return: os.path.getsize(out_file) in bytes
        """
        if not os.path.isfile(out_file):
            try:
                with gzip.open(in_file, 'rb') as f_in, open(out_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            except Exception as e:
                logger.error(f'gzip failed on file: {in_file}: {e}')
                print(f'gzip failed on file: {in_file}: {e}')
                file_size = None
            else:
                file_size = os.path.getsize(out_file)
        else:
            print(f'Uncompressed output file exists: {out_file}. Skipping.')
            file_size = os.path.getsize(out_file)
        return file_size

    def file_size_from_url(self, url):
        """
        Method to acquire size of a file without download
        :param: url
        :returns: size in bytes (int)
        """
        url_size = np.nan
        try:
            with contextlib.closing(request.urlopen(url)) as ul:
                url_size = ul.length
        except HTTPError as http_err:
            logger.error(f'ERROR: {http_err}: URL: {url}')
        except Exception as e:
            logger.error(f'ERROR {e}: URL: {url}')
        return url_size

    def download_from_url(self, url, download_dir, extract=True, delete_after_extract=False, ext_list=None):
        """
        :param url: cloud storage location URL
        :param download_dir: path-like object representing file path.
        :param extract: extract file if compressed
        :param delete_after_extract: if file is an archive, delete file after extraction.
        :param ext_list: list of allowed extensions, for example '.json.gz' or '.zip'
        :return: file path of output file
        """
        output_file_name = os.path.basename(url)
        if ext_list is not None:
            ext_in_url = [xt for xt in ext_list if xt in url]
            if len(ext_in_url) > 0:
                xt = ext_in_url[0]
                output_file_name = f'{output_file_name.split(xt, maxsplit=1)[0]}{xt}'
        output_file = os.path.join(download_dir, output_file_name)
        if os.path.exists(download_dir):
            if not os.path.exists(output_file):
                try:
                    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=output_file_name) as t:
                        request.urlretrieve(url, filename=output_file, reporthook=t.update_to)
                except HTTPError as http_err:
                    print(http_err)
                    logger.error(f'Download failed for URL: {url}'
                                 f' {http_err}')
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f'Download failed for URL: {url}'
                                 f' {e}')
                else:
                    logger.info(f'Download complete: {output_file}.')
            else:
                logger.info(f'File exists: {output_file}')
            # Unpacking
            output_file_path = output_file
            if os.path.exists(output_file) and extract:
                file_parts = os.path.splitext(output_file)
                xt = file_parts[-1]
                if xt in ['.gz']:
                    print(f'Extracting from {xt} archive.')
                    out_file = file_parts[0]
                    file_size = self.unzip(in_file=output_file, out_file=out_file)
                    if file_size is not None:
                        output_file_path = out_file
                        if delete_after_extract:
                            os.unlink(output_file)
                            logger.info(f'Deleted compressed file {output_file}')
                elif xt in ['.json', '.csv', '.pickle', '.parquet', '.ckpt', '.pth']:
                    print(f'Created {xt} file.')
                else:
                    print(f'File: {xt} loaded.')
                    logger.warning(f'File extension is unexpected {xt}.')
            elif os.path.exists(output_file) and not extract:
                output_file_path = output_file
        else:
            logger.error(f'Output directory {download_dir} does not exist.')
            output_file_path = None
        return output_file_path

    def search_file_tree(self, top_dir, file_pattern):
        """
        Search directory recursively for file pattern
        Parameters
        ----------
        top_dir: str, top file directory
        file_pattern: str, file pattern e.g. '*part.jpg'
        Returns
        -------
        output_df: pd.DataFrame with all files
        """
        output_df = None
        file_list = []
        print(f'Searching for files from top-dir "{top_dir}"')
        if os.path.exists(top_dir):
            file_list = glob.glob(os.path.join(top_dir, '**', f'{file_pattern}'), recursive=True)
        else:
            print(f'top_dir: {top_dir} does not exist.')
        if len(file_list) > 0:
            file_name_list = [os.path.basename(file) for file in file_list]
            file_dir_list = [os.path.split(file)[0] for file in file_list]
            file_dict = {'file_name': file_name_list,
                         'file_dir': file_dir_list,
                         'file': file_list}
            output_df = pd.DataFrame(file_dict)
        return output_df