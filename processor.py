import redis
import json
import requests
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akaskhoone.settings.base')
application = get_wsgi_application()

r = redis.StrictRedis(host='localhost', port=6379, db=0)

while True:
    notify = json.loads(r.brpop("notifications")[1].decode())
    for user_id in notify.get("users_notified"):
        requests.post(url="http://127.0.0.1:8000/private/", json={
            "notify_type": notify.get("notify_type"),
            "user_id": notify.get("user_id"),
            "post_id": notify.get("post_id"),
            "user_notified_id": user_id
        })
