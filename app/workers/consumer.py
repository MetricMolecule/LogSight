import asyncio

from redis.exceptions import ResponseError

from app.core.redis import redis

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
            print(response)


if __name__ == "__main__":
    asyncio.run(consume())
