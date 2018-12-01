from django.test import TestCase

# Create your tests here.
def tearDown(self):
    from django_redis import get_redis_connection
    get_redis_connection("default").flushall()
