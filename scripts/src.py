import cv2
import numpy as np
import pickle
from utils import load_gif, load_gif_gray
import cyvlfeat as vlfeat
import sklearn.metrics.pairwise as sklearn_pairwise

debugging_flag=True

def build_vocabulary(image_paths, vocab_size):
    """
    This function will sample SIFT descriptors from the training images,
    cluster them with kmeans, and then return the cluster centers.
    """
    dim = 128      # length of the SIFT descriptors that you are going to compute.
    vocab = np.zeros((vocab_size,dim))
    
    N = len(image_paths)
    assert N > 0, 'there must be at least one image path!'
    
    # smapled features
    before_clustered = 200000
    sampled_features = np.empty((before_clustered, dim))
    count, visited = 0, 0
    while count < before_clustered:
        index = np.random.randint(N)
        img = load_gif_gray(image_paths[index])
        
        frames, descriptors = vlfeat.sift.dsift(img, fast=debugging_flag, step=15)
        added_num = min(before_clustered-count, descriptors.shape[0])
        sampled_features[count:count+added_num, :] = descriptors[:added_num, :]
        
        count = count + added_num
        visited = visited + 1
    
    # clustering
    vocab = vlfeat.kmeans.kmeans(sampled_features, vocab_size)
    return vocab

def get_bags_of_sifts(image_paths, vocab_filename):
    # load vocabulary
    with open(vocab_filename, 'rb') as f:
        vocab = pickle.load(f)

    # dummy features variable
    feats = []
    N = len(image_paths)
    vocab_size = vocab.shape[0]
    
    feats = np.empty((N, vocab_size))
    list_descriptors = []
    images_per_cluster = 1000 # calc the kmeans_quantize for multiple images once
    count = 0
    for i in range(N):
        img = load_gif_gray(image_paths[i])
        frames, descriptors = vlfeat.sift.dsift(img, fast=debugging_flag, step=5)
        descriptors = descriptors.astype(np.float64)
        
        list_descriptors.append(descriptors)
        
        if i % images_per_cluster == images_per_cluster-1 or i == N-1:
            # create the split indexs
            indexs = [descriptor.shape[0] for descriptor in list_descriptors]
            indexs = np.cumsum(indexs[:-1]) # make the size is equal
            
            # vstack the descriptors
            stacked_descriptors = np.vstack(list_descriptors)
            assignments = vlfeat.kmeans.kmeans_quantize(stacked_descriptors, vocab)
            
            # split
            splited_assignments = np.split(assignments, indexs)
            
            # histogram
            for assign in splited_assignments:
                values, bins = np.histogram(assign, bins=np.arange(vocab_size+1), density=True)
                feats[count, :] = values
                count = count + 1
            
            # reset the list
            list_descriptors = []

    return feats

def nearest_neighbor_classify(train_image_feats, test_image_feats,
    metric='euclidean'):

    # compute the distances
    if metric == 'euclidean':
        pair_distances = sklearn_pairwise.pairwise_distances(test_image_feats, train_image_feats)
    else:
        pair_distances = sklearn_pairwise.pairwise_distances(test_image_feats, train_image_feats)
        
    # find the nearest neighbour classifier
    indexs = np.argsort(pair_distances, axis=1)
    return indexs