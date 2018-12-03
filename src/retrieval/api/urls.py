from django.urls import path

from . import views

urlpatterns = [
    path('update_vocab_tree', views.update_vocab_tree, name='update_vocab_tree'),
    path('update_images', views.update_images, name='update_images'),
    path('sample_query', views.sample_query, name='sample_query'),
    path('text_query', views.text_query, name='text_query')
]
