from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt
import numpy as np

from api.models import *
from api.utils import get_redis_key, PickledRedis
import api.services as sv

import json
import os.path as osp
import pickle
import codecs

def index(request):
    image = Image(image_id='1', url='https://38.media.tumblr.com/9e6fcb37722bf01996209bdf76708559/tumblr_np9xo74UgD1ux4g5vo1_250.gif', description='a boy is happy parking and see another boy')
    cache.set(image.get_key(), image)
    image = cache.get('image_1')   
    return HttpResponse(image.url)

def list_all(request):
    tree_node = VocabTreeNode(node_id=13, children_ids=[2,3], descriptor=np.array([1,23]))
    cache.set(get_redis_key(tree_node), tree_node)
    node = cache.get(get_redis_key(tree_node))
    return HttpResponse(node.descriptor.shape)

@csrf_exempt
def update_vocab_tree(request):
    if request.method == 'POST':
        post_data = request.POST
        node_descriptors = pickle.loads(codecs.decode(post_data['nodes'].encode(), "base64"))
        tree_nodes = pickle.loads(codecs.decode(post_data['tree'].encode(), "base64"))
        imagesInLeaves = pickle.loads(codecs.decode(post_data['imagesInLeaves'].encode(), "base64"))
        doc = pickle.loads(codecs.decode(post_data['doc'].encode(), "base64"))

        # reformation
        invert_indexs = {}
        for key, value in imagesInLeaves.items():
            invert_indexs[key] = {}
            for image_path, occurance in value.items():
                image_id = osp.split(image_path)[-1].split('.')[0]
                image_id = int(image_id)
                invert_indexs[key][image_id] = occurance

        nodes = {}
        for key, value in tree_nodes.items():
            nodes[key] = {'children_ids': value, 'descriptor': node_descriptors[key]}

        image_indexs = {}
        for key, value in doc.items():
            image_id = osp.split(key)[-1].split('.')[0]
            image_id = int(image_id)
            image_indexs[image_id] = value

        print('Start insert info into Redis')
        sv.update_nodes(nodes)
        sv.update_invert_indexs(invert_indexs)
        sv.update_image_indexs(image_indexs)
    return HttpResponse()

@csrf_exempt
def update_images(request):
    if request.method == 'POST':
        csv_file = request.FILES['images.csv']
        csv_data = codecs.decode(csv_file.read(), 'utf-8')
        sv.update_images(csv_data)
    return HttpResponse()

@csrf_exempt
def sample_query(request):
    if request.method == 'POST':
        gif_file = request.FILES['query.gif']
        gif_data = gif_file.read()
        images = sv.sample_query(gif_data)
        images = [image.as_dict() for image in images]
        return JsonResponse(images, safe=False)
    return HttpResponse()
