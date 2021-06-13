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

OVERWRITE = False  # Overwrite file if already downloaded
SAVE_DIR = 'E:/USGS DEM TIFF'  # Download destination

BUCKET = 'prd-tnm'
PREFIX = 'StagedProducts/Elevation/13/TIFF/'
REGEX_PATTERN = r'.*([n|s]\d{2}[e|w]\d{3})/USGS_13_\1\.tif$'

# Initialize boto3 client in anonymous configuration
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=BUCKET, Prefix=PREFIX)

# Collect list of files to download and file sizes
file_keys = []
file_sizes = []
for page in pages:
    for obj in page['Contents']:
        if re.match(REGEX_PATTERN, obj['Key']):
            file_keys.append(obj['Key'])
            file_sizes.append(obj['Size'])

file_count = len(file_keys)
total_size = sum(file_sizes)

print('Beginning download...\n')
progress_bytes = 0
for file_num, file_info in enumerate(zip(file_keys, file_sizes), 1):
    file_key, file_size = file_info
    save_name = file_key.replace(PREFIX, '')
    save_path = os.path.join(SAVE_DIR, save_name)
    print('File {} of {}'.format(file_num, file_count))
    print(file_key)
    print(save_path)
    print(file_size, 'bytes')

    # Download file
    save_dirname = os.path.dirname(save_path)
    if not os.path.isfile(save_path) or OVERWRITE:
        if not os.path.isdir(save_dirname):
            os.mkdir(save_dirname)
        s3.download_file(BUCKET, file_key, save_path)
    
    # Display download progress %
    progress_bytes += file_size
    progress_pct = 100 * progress_bytes/total_size
    print('Progress: {:.2f}% ({} of {} bytes)\n'
              .format(progress_pct, progress_bytes, total_size))