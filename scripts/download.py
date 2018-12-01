#!/usr/bin/python
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from urllib import request
from glob import glob
from random import shuffle

import os
import os.path as osp
import logging
import csv
import pickle

logging.basicConfig(filename='test.log', level=logging.DEBUG)

data_path = osp.join('..','data')
csv_path = osp.join(data_path, 'csv')
csv_files = glob(osp.join(csv_path, '*.csv'))
relation_file = osp.join(data_path, 'relation.pkl')
limit_each_category = 3000

def create_download_task(url, file_name):
    # download the csv to the file system
    def download_csv():
        logging.debug('downloding the gif from the url: {:s}, file name: {:s}'.format(url, file_name))
        with open(file_name, 'wb') as f:
            f.write(request.urlopen(url).read())
    return download_csv

def main():
    all_images = [] # [{'id': ..., 'category': ..., 'url': ..., 'description': ...}]
    # get all the csv files
    logging.info('Serval csv file for downloading the GIFs: {:s}'.format(str(csv_files)))
    for csv_file in csv_files:
        category_name = osp.split(csv_file)[-1][:-4]
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            image_list = list(reader)
        # add the category info
        shuffle(image_list)
        image_list = image_list[:limit_each_category]
        reformat = [{'id': image[0], 'category': category_name, \
            'url': image[1], 'description': image[2]} for image in image_list] 
        all_images.extend(reformat)
    
    # dump the relation dictionary
    with open(relation_file, 'wb') as f:
        pickle.dump(all_images, f)
        print('{:s} saved'.format(relation_file))

    # check and create the directory for each category
    directory_names = set([image['category'] for image in all_images])
    for directory_name in directory_names:
        directory = osp.join(data_path, directory_name)
        if not osp.exists(directory):
            os.makedirs(directory)

    # get and save all the images
    futures = []
    with ThreadPoolExecutor(max_workers=15) as pool:
        for image in all_images:
            image_file = osp.join(data_path, image['category'], image['id']+'.gif')
            future = pool.submit(create_download_task(image['url'], image_file))
            futures.append(future)
        wait(futures, return_when=ALL_COMPLETED)
        logging.info('finish downloading all the GIFs')

if __name__ == '__main__':
    main()
