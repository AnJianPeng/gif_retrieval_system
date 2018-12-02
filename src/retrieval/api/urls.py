from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list_all', views.list_all, name='list_all'),
    path('update_vocab_tree', views.update_vocab_tree, name='update_vocab_tree'),
    path('update_images', views.update_images, name='update_images'),
    path('sample_query', views.sample_query, name='sample_query')
]
