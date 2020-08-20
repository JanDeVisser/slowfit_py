from django.contrib.auth.models import AnonymousUser, User
from django.test.client import Client

USERNAME = "jan"
USER_PASSWORD = "top_secret"
USER_EMAIL = "jan@slowfit.com"


def create_user():
    user = User.objects.create_user(username=USERNAME, email=USER_EMAIL, password=USER_PASSWORD)
    return user


def login(client: Client):
    client.login(username=USERNAME, password=USER_PASSWORD)
