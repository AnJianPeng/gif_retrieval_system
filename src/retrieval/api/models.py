from django.db import models

# Create your models here.
class Image(models.Model):
    image_id = models.IntegerField(default=1, )
    url = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
