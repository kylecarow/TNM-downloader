"""
Kyle Carow
kylecarow@gmail.com
https://github.com/kylecarow

TNM_downloader.py
Downloading script for the 1/3 arc-second USGS DEM (.tif)
http://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Elevation/13/TIFF/current/
"""

import os
import re
from math import floor, ceil
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from typing import Tuple

XMIN = -109.060253
XMAX = -102.041524
YMIN = 36.992426
YMAX = 41.003444


def nsew_to_decimal(nsew_str: str) -> Tuple[int, int]:
    """example: n72w157 to (72, -157)"""
    lat_sign = 1 if nsew_str[0] == "n" else -1
    lon_sign = 1 if nsew_str[3] == "e" else -1
    lat_str = nsew_str[1:3]
    lon_str = nsew_str[4:7]
    return lat_sign * int(lat_str), lon_sign * int(lon_str)


def within_bounding_box(lat: int, lon: int) -> bool:
    return (lat in range(*sorted((int(YMIN), int(YMAX) + 1)))) and (
        lon in range(*sorted((int(XMIN), int(XMAX) + 1)))
    )


if __name__ == "__main__":
    OVERWRITE = False  # Overwrite file if already downloaded
    # SAVE_DIR = "/home/kylecarow/Repositories/elevation-map/USGS_13_DEM/"  # Download destination
    SAVE_DIR = "./USGS_13_DEM/"  # Download destination

    # National map bucket
    BUCKET = "prd-tnm"
    # Location of TIFF files in bucket
    PREFIX = "StagedProducts/Elevation/13/TIFF/current/"
    # Regex pattern to match files
    REGEX_PATTERN = r"USGS_13_([n|s]\d{2}[e|w]\d{3})\.(tif|xml)$"

    # Initialize boto3 client in anonymous configuration
    s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    # Initialize paginator with TIFF file location
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET, Prefix=PREFIX)

    # Collect list of files to download and file sizes
    file_keys = []
    file_sizes = []
    for page in pages:
        for obj in page["Contents"]:
            # If object in page is TIFF file of proper format
            match = re.search(REGEX_PATTERN, obj["Key"])
            if match:
                lat, lon = nsew_to_decimal(match.group(0)[8:-4])
                if within_bounding_box(lat, lon):
                    # Collect object information
                    file_keys.append(obj["Key"])
                    file_sizes.append(obj["Size"])

    # Generate information on files for downloader UI output
    file_count = len(file_keys)
    total_bytes = sum(file_sizes)

    # Download listed files
    print("Beginning download...\n")
    progress_bytes = 0
    for file_num, file_info in enumerate(zip(file_keys, file_sizes), 1):
        file_key, file_size = file_info
        # Extract "USGS_13_ ... .tif" filename and generate save location
        file_name = re.search(REGEX_PATTERN, file_key).group(0)
        save_path = os.path.join(SAVE_DIR, file_name)

        # Display file information
        print(f"File {file_num} of {file_count}")
        print(file_key)
        print(save_path)
        print(file_size, "bytes")

        # Download file
        save_dirname = os.path.dirname(save_path)
        # If file isn't already downloaded, or if overwriting is okay
        if not os.path.isfile(save_path) or OVERWRITE:
            # Make directory if necessary
            if not os.path.isdir(save_dirname):
                os.makedirs(save_dirname)
            s3.download_file(BUCKET, file_key, save_path)

        # Display download progress %
        progress_bytes += file_size
        progress_pct = 100 * progress_bytes / total_bytes
        print(
            f"Progress: {progress_pct:.2f}% ({progress_bytes} of {total_bytes} bytes)\n"
        )
