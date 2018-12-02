from django.core.cache import cache
import cyvlfeat as vlfeat
import numpy as np

from api.models import *
from api.utils import get_redis_key, PickledRedis, load_gif_gray

import csv
from io import BytesIO, StringIO
import math

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

def get_image_index(image_id):
    new_index = ImageIndex(image_id=image_id)
    new_index = cache.get(get_redis_key(new_index))
    return new_index

def get_node(node_id):
    new_node = VocabTreeNode(node_id=node_id)
    new_node = cache.get(get_redis_key(new_node))
    return new_node
'''
Function to lookup a SIFT descriptor in the vocabulary tree, returns a leaf cluster
descriptor: one descriptor in the query image
node: node_id in the vocab tree
'''
def lookup(descriptor, node):
    D = float('inf')
    goto = None
    tree_node = get_node(node)
    for child_id in tree_node.children_ids:
        child_node = get_node(child_id)
        dist = np.linalg.norm([child_node.descriptor - descriptor])
        if D > dist:
            D = dist
            goto = child_id
    if get_node(goto).children_ids == []:
        return goto
    return lookup(descriptor, goto)

# This function returns the weight of a leaf node
def weight(leafID, N):
    print(leafID)
    invert_index = get_invert_index(leafID)
    return math.log1p(N/1.0*len(invert_index.image_id_freqs))

'''
return: list of Image
'''
def sample_query(query_image):
    N = 5000 # assume that the image amout in the db is 5000
    q = {}
    f = BytesIO(query_image)
    img = load_gif_gray(f)
    kp, des = vlfeat.sift.dsift(img, fast=True, step=5)
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
    print(q)
    return [get_image(image_id) for image_id in [11, 41257]]

# Returns the scores of the images in the dataset
def getScores(q, N, dataset_paths):
    scores = {}
    n = 0
    count = 0
    curr = [float("inf"),float("inf"),float("inf"),float("inf") ]
    currimg = ["","","",""]
    for img in dataset_paths:
        scores[img] = 0
        for leafID in imagesInLeaves:
            if leafID in doc[img] and leafID in q:
                scores[img] += math.fabs(q[leafID] - doc[img][leafID])
            elif leafID in q and leafID not in doc[img]:
                scores[img] += math.fabs(q[leafID])
            elif leafID not in q and leafID in doc[img]:
                scores[img] += math.fabs(doc[img][leafID])
            if scores[img] > curr[-1]:
                break

        if scores[img] <= curr[0]:
            currimg[3], curr[3] = currimg[2], curr[2]
            currimg[2], curr[2] = currimg[1], curr[1]
            currimg[1], curr[1] = currimg[0], curr[0]
            currimg[0], curr[0] = img, scores[img]
        elif scores[img] > curr[0] and scores[img] <= curr[1]:
            currimg[3], curr[3] = currimg[2], curr[2]
            currimg[2], curr[2] = currimg[1], curr[1]
            currimg[1], curr[1] = img, scores[img]
        elif scores[img] > curr[1] and scores[img] <= curr[2]:
            currimg[3], curr[3] = currimg[2], curr[2]
            currimg[2], curr[2] = img, scores[img]
        elif scores[img] > curr[2] and scores[img] <= curr[3]:
            currimg[3], curr[3] = img, scores[img]
        n = n + 1
        if n >= N:
            break
    return currimg
