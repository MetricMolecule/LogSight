import asyncio

from redis.exceptions import ResponseError

from app.core.database import get_db
from app.core.redis import redis
from app.services.log_service import save_log

STREAM = "logs"
GROUP = "logsight-workers"
CONSUMER = "worker-1"


async def create_group():
    try:
        await redis.xgroup_create(
            STREAM,
            GROUP,
            id="0",
            mkstream=True,
        )
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise


async def consume():
    await create_group()

    print("Worker started...")

    while True:
        response = await redis.xreadgroup(
            groupname=GROUP,
            consumername=CONSUMER,
            streams={STREAM: ">"},
            count=1,
            block=5000,
        )

        if response:
            stream_name, messages = response[0]

            for message_id, fields in messages:
                print(f"Received {message_id}")

                try:
                    with get_db() as db:
                        save_log(db, fields)

                    await redis.xack(
                        STREAM,
                        GROUP,
                        message_id,
                    )

                    print(f"Stored and ACKed {message_id}")

                except Exception as e:
                    print(f"Failed: {e}")


if __name__ == "__main__":
    asyncio.run(consume())
