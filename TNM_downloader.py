'''
Kyle Carow
kylecarow@gmail.com
https://github.com/kylecarow

TNM_downloader.py
Downloading script for the 1/3 arc-second USGS DEM (.tif)
'''

import os
import re
import boto3
from botocore import UNSIGNED
from botocore.client import Config

SAVE_DIR = 'E:/USGS DEM TIFF' # Download destination
BUCKET = 'prd-tnm'
PREFIX = 'StagedProducts/Elevation/13/TIFF/'
REGEX_PATTERN = r'.*([n|s]\d{2}[e|w]\d{3})/USGS_13_\1\.tif$'

# Initialize boto3 client in anonymous configuration
s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
s3_client = s3.meta.client
paginator = s3_client.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=BUCKET, Prefix=PREFIX)

# Collect list of files to download and file sizes
files_to_download = []
file_sizes = []
for page in pages:
    for obj in page['Contents']:
        if re.match(REGEX_PATTERN, obj['Key']):
            files_to_download.append(obj['Key'])
            file_sizes.append(obj['Size'])

total_size = sum(file_sizes)

print('Beginning download...\n')
progress_bytes = 0
for file_key, file_size in zip(files_to_download, file_sizes):
    save_name = file_key.replace(PREFIX, '')
    save_path = os.path.join(SAVE_DIR, save_name)
    print(file_key, '\n', save_path, sep='')

    # Download file
    save_dirname = os.path.dirname(save_path)
    if not os.path.isdir(save_dirname):
        os.mkdir(save_dirname)
    s3_client.download_file(BUCKET, file_key, save_path)
    
    # Display download progress %
    progress_bytes += file_size
    progress_pct = 100 * progress_bytes/total_size
    print('Progress: \033[92m{:.2f}%\033[0m ({} of {} bytes)\n'
              .format(progress_pct, progress_bytes, total_size))