import numpy as np
import cv2
import os.path as osp
from glob import glob
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.metrics import confusion_matrix

def load_gif_gray(path):
    im = Image.open(path)
    n_frames = im.n_frames
    count = 0
    
    ret = []
    while count < n_frames:
        im.seek(count)
        imframe = im.copy()
        if count == 0:
            palette = imframe.getpalette()
        else:
            imframe.putpalette(palette)
            
        # add the interesting frames
        if count == 0:
            ret.append(imframe)
        elif count == n_frames // 2:
            ret.append(imframe)
        elif count == n_frames // 4:
            ret.append(imframe)
        elif count == n_frames * 3 // 4:
            ret.append(imframe)
        elif count == n_frames-1:
            ret.append(imframe)
        
        count = count+1
    # convert to gray
    ret = [np.array(imframe.convert('L')) for imframe in ret]
    return ret

def get_image_directories(data_path, categories):
    return [osp.join(data_path, category) for category in categories]

def load_images_paths(limit_each_category, paths):
    """
    try to load paths for each category as much as limit_each_category
    """
    image_paths = []
    image_labels = []
    for path in paths:
        category = osp.split(path)[-1]
        files = glob(osp.join(path, '*.gif'))[:limit_each_category]
        image_paths.extend(files)
        image_labels.extend([category]*len(files))
    
    return image_paths, image_labels

def show_results(train_image_paths, test_image_paths, train_labels, test_labels,
    categories, abbr_categories, predicted_categories):
  """
  shows the results
  :param train_image_paths:
  :param test_image_paths:
  :param train_labels:
  :param test_labels:
  :param categories:
  :param abbr_categories:
  :param predicted_categories:
  :return:
  """
  cat2idx = {cat: idx for idx, cat in enumerate(categories)}

  # confusion matrix
  y_true = [cat2idx[cat] for cat in test_labels]
  y_pred = [cat2idx[cat] for cat in predicted_categories]
  cm = confusion_matrix(y_true, y_pred)
  cm = cm.astype(np.float) / cm.sum(axis=1)[:, np.newaxis]
  acc = np.mean(np.diag(cm))
  print(cm)
  plt.figure()
  plt.imshow(cm, interpolation='nearest', cmap=plt.cm.get_cmap('jet'))
  plt.title('Confusion matrix. Mean of diagonal = {:4.2f}%'.format(acc*100))
  tick_marks = np.arange(len(categories))
  plt.tight_layout()
  plt.xticks(tick_marks, abbr_categories, rotation=45)
  plt.yticks(tick_marks, categories)