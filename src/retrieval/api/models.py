from django.db import models
import pickle

# Create your models here.
class Image(models.Model):
    image_id = models.IntegerField(default=1, primary_key=True)
    url = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def as_dict(self):
        return dict(
                image_id=self.image_id,
                url=self.url,
                description=self.description)

class VocabTreeNode(models.Model):
    node_id = models.IntegerField(default=1, primary_key=True)
    _children_ids = models.BinaryField()
    _descriptor = models.BinaryField()

    def set_children_ids(self, data):
        self._children_ids = pickle.dumps(data)

    def get_children_ids(self):
        return pickle.loads(self._children_ids)

    def set_descriptor(self, data):
        self._descriptor = pickle.dumps(data)

    def get_descriptor(self):
        return pickle.loads(self._descriptor)

    children_ids = property(get_children_ids, set_children_ids)
    descriptor = property(get_descriptor, set_descriptor)

class InvertIndex(models.Model):
    node_id = models.IntegerField(default=1, primary_key=True)
    image_id_freqs = models.BinaryField()

class ImageIndex(models.Model):
    image_id = models.IntegerField(default=1, primary_key=True)
    node_weights = models.BinaryField()
