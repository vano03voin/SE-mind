import sys
import requests
from loguru import logger

def send_bug_to_bug_server(message):
    webhook_url = "https://discord.com/api/webhooks/1287746805349744672/5RlKjD-W2Z1-Q0X9PckXZ8JuEIsFgHrZxxLZHH4LcaF-6yQF5xUzLEJlRel5UhbI8yoU"
    data = {
        "content": f"``` {message[-1990:]} ```",
        #"username": __file__
    }
    requests.post(webhook_url, json=data)

logger.remove()

logger.add(
    send_bug_to_bug_server,
    level="ERROR",
    filter=lambda record: record["level"].no >= 40
)
