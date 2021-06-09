'''
Kyle Carow
kylecarow@gmail.com
https://github.com/kylecarow
'''

from urllib import request
import os
import shutil
import zipfile

THIS_DIR = os.path.dirname(__file__)
SAVE_DIR = 'E:/USGS DEM/grid'

urls = []
with open(os.path.join(THIS_DIR, 'urls.txt')) as url_file:
    for line in url_file.readlines():
        urls.append(line)

for i, url in enumerate(urls, 1):
    filename = url.replace('\n', '').rsplit('/', 1)[-1]
    filepath = os.path.join(SAVE_DIR, filename)

    print(filename)
    print('File {} of {}\n'.format(i, len(urls)))

    with request.urlopen(url) as response, open(filepath, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(filepath, 'r') as zip_file:
        zip_file.extractall(filepath.replace('.zip', ''))
    os.remove(filepath)