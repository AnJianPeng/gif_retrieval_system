from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache

from api.models import Image

def index(request):
    image = Image(image_id='1', url='https://38.media.tumblr.com/9e6fcb37722bf01996209bdf76708559/tumblr_np9xo74UgD1ux4g5vo1_250.gif', description='a boy is happy parking and see another boy')
    cache.set(image.get_key(), image)
    image = cache.get('image_1')   
    return HttpResponse(image.url)


