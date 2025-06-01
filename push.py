from queue import Queue
import time
from async_utils import delay
from config import Config, Push
import requests

from logger import log_info

q = []


def new_push(message: str):
    q.append(message)


def immediate_push(message: str, pushes: list[Push]):
    do_push([message], pushes)


def process_queue(conf: Config):
    while True:
        try:
            if len(q) > 0:
                do_push(q, conf.pushes)
            delay(10)
        except Exception as e:
            log_info(f"Error processing push queue: {e}")


def do_push(messages: list[str], pushes: list[Push]):
    log_info(f"Sending push notification: {messages}")
    for push in pushes:
        if push.enabled and push.app in PUSH_APPS:
            try:
                PUSH_APPS[push.app](push, messages)
            except Exception as e:
                log_info(f"Failed to send push notification via {push.app}: {e}")


# Apps


def push_bark(push: Push, messages: list[str]):
    url = push.url
    body = ""
    if len(messages) == 1:
        body = messages[0]
    elif len(messages) > 1:
        count = 1
        for message in messages:
            body += f"#{count}\n{message}\n"
            count += 1
    else:
        return
    payload = {
        "title": "Error Notification",
        "body": message,
        "group": "Cloud Map Spider",
        "sound": "default",
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        log_info(f"Push notification sent successfully: {response.json()}")
    else:
        log_info(
            f"Failed to send push notification: {response.status_code} {response.text}"
        )


PUSH_APPS = {
    "bark": push_bark,
}
