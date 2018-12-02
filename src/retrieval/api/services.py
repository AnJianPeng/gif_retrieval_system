from django.core.cache import cache
import cyvlfeat as vlfeat

from api.models import *
from api.utils import get_redis_key, PickledRedis, load_gif_gray

import csv
from io import StringIO

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
#
## Function to lookup a SIFT descriptor in the vocabulary tree, returns a leaf cluster
#def lookup(descriptor, node):
#    D = float("inf")
#    goto = None
#    for child in tree[node]:
#        dist = np.linalg.norm([nodes[child] - descriptor])
#    if D > dist:
#        D = dist
#        goto = child
#    if tree[goto] == []:
#        return goto
#    return lookup(descriptor, goto)
#
#'''
#
#'''
#def match(query_image):
#    q = {}
#    img = load_gif_gray(filename)
#    kp, des = sift(img, fast=True, step=5)
#    for d in des:
#        leafID = lookup(d, 0)
#    if leafID in q:
#        q[leafID] += 1
#    else:
#        q[leafID] = 1
#    s = 0.0
#    for key in q:
#        q[key] = q[key]*weight(key, N, imagesInLeaves)
#        s += q[key]
#    for key in q:
#        q[key] = q[key]/s
#    return getScores(q, N, dataset_paths)
#
