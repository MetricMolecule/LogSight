import random
from datetime import datetime

import requests

URL = "http://127.0.0.1:8000/logs"

services = [
    "auth-service",
    "payment-service",
    "notification-service",
    "inventory-service",
]

levels = [
    "INFO",
    "WARN",
    "ERROR",
]

messages = [
    "User login",
    "Payment failed",
    "Database timeout",
    "Inventory updated",
    "Email sent",
]

for i in range(20):
    payload = {
        "service": random.choice(services),
        "level": random.choice(levels),
        "message": random.choice(messages),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": f"req-{i}",
        "user_id": f"user-{random.randint(1, 15)}",
        "metadata": {
            "iteration": i,
            "ip": "127.0.0.1",
        },
    }

    r = requests.post(URL, json=payload)

    print(i, r.status_code)
