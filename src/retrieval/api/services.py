from django.core.cache import cache
import cyvlfeat as vlfeat
import numpy as np

from api.models import *
from api.utils import get_redis_key, PickledRedis, load_gif_gray

import csv
from io import BytesIO, StringIO
import math
import time
import os.path as osp
import pickle
from heapq import heappush, heappop

# init the variables used from the file system
data_path = osp.join(osp.join('..', '..'), 'data')
setup_data_path = osp.join(data_path, 'setup')
vocab_tree = {} # node_id: {descriptor: ..., children_ids: ...}
with open(osp.join(setup_data_path, 'tree.pkl'), 'rb') as f1:
    with open(osp.join(setup_data_path, 'nodes.pkl'), 'rb') as f2:
        tree = pickle.load(f1)
        node_descriptors = pickle.load(f2)

        for key, value in tree.items():
            vocab_tree[key] = {'children_ids': value, 'descriptor': node_descriptors[key]}

invert_indexs = {} # leaf_node_id: { image_id: occurance}
with open(osp.join(setup_data_path, 'imagesInLeaves.pkl'), 'rb') as f:
    imagesInLeaves = pickle.load(f)
    for key, value in imagesInLeaves.items():
        invert_indexs[key] = {}
        for image_path, occurance in value.items():
            image_id = osp.split(image_path)[-1].split('.')[0]
            invert_indexs[key][image_id] = occurance

image_indexs = {} # image_id: {leaf_node_id: weighted_occurance}
with open(osp.join(setup_data_path, 'doc.pkl'), 'rb') as f:
    doc = pickle.load(f)
    for key, value in doc.items():
        image_id = osp.split(key)[-1].split('.')[0]
        image_indexs[image_id] = value

def update_nodes(nodes):
    for key, value in nodes.items():
        new_node = VocabTreeNode(node_id=key, children_ids=value['children_ids'], descriptor=value['descriptor'])
        cache.set(get_redis_key(new_node), new_node, timeout=None)

def update_invert_indexs(invert_indexs):
    for key, value in invert_indexs.items():
        new_index = InvertIndex(node_id=key, image_id_freqs=value)
        cache.set(get_redis_key(new_index), new_index, timeout=None)

def update_image_indexs(image_indexs):
    for key, value in image_indexs.items():
        new_index = ImageIndex(image_id=key, node_weights=value)
        cache.set(get_redis_key(new_index), new_index, timeout=None)

def update_images(csv_str):
    f = StringIO(csv_str)
    images = csv.reader(f)
    images = list(images)
    for image in images:
        new_image = Image(image_id=image[0], url=image[1], description=image[2])
        cache.set(get_redis_key(new_image), new_image, timeout=None)

def get_invert_index(node_id):
    new_index = InvertIndex(node_id=node_id)
    new_index = cache.get(get_redis_key(new_index))
    return new_index

def get_image(image_id):
    new_image = Image(image_id=image_id)
    new_image = cache.get(get_redis_key(new_image))
    return new_image

# get image local address
def get_image_local(image_id):
    prefix = 'http://localhost:8000/static/'
    url = prefix + str(image_id) + '.gif'
    image = Image(image_id=image_id, url=url, description='')
    return image

def get_image_index(image_id):
    new_index = ImageIndex(image_id=image_id)
    new_index = cache.get(get_redis_key(new_index))
    return new_index

def get_node(node_id):
    total_call = total_call + 1
    new_node = VocabTreeNode(node_id=node_id)
    new_node = cache.get(get_redis_key(new_node))
    return new_node

'''
this class is used to init the vocabluray tree from the vocabulary tree
We use pickle in the Model serilization, which will slow the process greatly
'''
class VocabTree:
    tree_nodes = {}
    invert_indexs = {}
    forward_indexs = {}
    def __init__(self):
        pass

'''
Function to lookup a SIFT descriptor in the vocabulary tree, returns a leaf cluster
descriptor: one descriptor in the query image
node: node_id in the vocab tree
'''
def lookup(descriptor, node):
    global vocab_tree
    D = float('inf')
    goto = None
    tree_node = vocab_tree[node]
    for child_id in tree_node['children_ids']:
        child_node = vocab_tree[child_id]
        dist = np.linalg.norm([child_node['descriptor'] - descriptor])
        if D > dist:
            D = dist
            goto = child_id
    if vocab_tree[goto]['children_ids'] == []:
        return goto
    return lookup(descriptor, goto)

# This function returns the weight of a leaf node
def weight(leafID, N):
    global invert_indexs
    invert_index = invert_indexs[leafID]
    return math.log1p(N/1.0*len(invert_index))

'''
return: list of Image
'''
def sample_query(query_image, augmented):
    global image_indexs
    N = len(image_indexs) # assume that the image amout in the db is 5000
    q = {}
    img = load_gif_gray(query_image)
    kp, des = vlfeat.sift.dsift(img, fast=True, step=5)
    start = time.time()
    for d in des:
        leafID = lookup(d, 0)
        if leafID in q:
            q[leafID] += 1
        else:
            q[leafID] = 1
    s = 0.0
    for key in q:
        q[key] = q[key]*weight(key, N)
        s += q[key]
    for key in q:
        q[key] = q[key]/s

    # create possible image ids
    possible_image_ids = []
    for leaf_node_id in q:
        possible_image_ids.extend(invert_indexs[leaf_node_id].keys())
    possible_image_ids = set(possible_image_ids)
    if not augmented:
        possible_image_ids = [image_id for image_id in possible_image_ids if '_' not in image_id]
    print(len(possible_image_ids))
    scores = getScores(q, N, possible_image_ids, 10)
    end = time.time()
    print(end-start)
    return [get_image_local(score[0]) for score in scores]

'''
Returns the scores of the images in the dataset
format: [(score, image_id)]
'''
def getScores(q, N, dataset_paths, target_num):
    global image_indexs
    scores = {}
    heap = [float('-inf')] * target_num
    for img in dataset_paths:
        cur_score = 0
        # check all leaf node occur in img and q 
        possible_leaf_ids = []
        possible_leaf_ids.extend(q.keys())
        possible_leaf_ids.extend(image_indexs[img].keys())
        possible_leaf_ids = set(possible_leaf_ids)

        for leafID in possible_leaf_ids:
            left = image_indexs[img].get(leafID, 0)
            right = q.get(leafID, 0)
            cur_score += math.fabs(left-right)
            if cur_score > -heap[0]:
                break

        # update the heap
        heappush(heap, -cur_score)
        if len(heap) > target_num:
            heappop(heap)
        scores[img] = cur_score
    res = sorted(scores.items(), key=lambda kv: (kv[1], kv[0]))
    return res[:target_num]
