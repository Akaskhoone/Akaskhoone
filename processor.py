import redis
import json
import requests
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akaskhoone.settings')
application = get_wsgi_application()

r = redis.StrictRedis(host='localhost', port=6379, db=0)

while True:
    new_notif = json.loads(r.brpop("notifications")[1].decode())
    user = new_notif["user"]
    if new_notif["type"] == "post":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "post",
            "user": new_notif["user"],
            "post": new_notif["post"]
        })
    elif new_notif["type"] == "like":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "like",
            "user": new_notif["user"],
            "post": new_notif["post"]
        })
    elif new_notif["type"] == "dislike":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "dislike",
            "user": new_notif["user"],
            "post": new_notif["post"]
        })
    elif new_notif["type"] == "comment":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "comment",
            "user": new_notif["user"],
            "post": new_notif["post"]
        })
    elif new_notif["type"] == "follow":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "follow",
            "user": new_notif["user"],
            "profile": new_notif["profile"]
        })
    elif new_notif["type"] == "unfollow":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "unfollow",
            "user": new_notif["user"],
            "profile": new_notif["profile"]
        })
    elif new_notif["type"] == "join":
        response = requests.post(url="http://127.0.0.1:8000/redis", json={
            "type": "join",
            "user": new_notif["user"],
        })
    print(response)