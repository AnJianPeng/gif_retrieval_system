import re
import pickle
from PIL import Image
import numpy as np

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_redis_key(model_object):
    return convert(model_object.__class__.__name__) + '_' + \
        str(getattr(model_object, model_object._meta.pk.name))

def load_gif_gray(image):
    im = Image.open(image)
    ret = np.array(im.convert('L'))
    return ret

class PickledRedis:
    connection = None

    def __init__(self, con):
        self.connection = con
    
    def get(self, name):
        pickled_value = self.connection.get(name)
        if pickled_value is None:
            return None
        else:
            return pickle.loads(pickled_value)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self.connection.set(name, pickle.dumps(value), ex, px, nx, xx)
