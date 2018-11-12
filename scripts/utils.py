import numpy as np
import cv2
import os.path as osp
from glob import glob
from PIL import Image

# by now, load function only load the first frame for the GIF
def load_gif(path):
    im = Image.open(path).convert("RGB")
    pix = np.array(im)
    return pix

def load_gif_gray(path):
    im = Image.open(path).convert("L")
    pix = np.array(im)
    return pix

def get_image_directories(data_path, categories):
    return [osp.join(data_path, category) for category in categories]

def load_images_paths(limit_each_category, paths):
    """
    try to load paths for each category as much as limit_each_category
    """
    image_paths = []
    for path in paths:
        files = glob(osp.join(path, '*.gif'))[:limit_each_category]
        image_paths.extend(files)
    
    return image_paths