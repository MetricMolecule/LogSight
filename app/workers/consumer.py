import asyncio
import json
from datetime import datetime

from redis.exceptions import ResponseError

from app.core.database import get_db
from app.core.redis import redis
from app.models import Log
from app.services.log_service import save_logs_bulk

STREAM = "logs"
DLQ_STREAM = "logs-dead-letter"

GROUP = "logsight-workers"
CONSUMER = "worker-1"

BATCH_SIZE = 100
MAX_RETRIES = 3


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


async def send_to_dlq(messages, reason):
    print(">>>>>>>> ENTERED DLQ FUNCTION <<<<<<<<")

    print(f"Messages = {len(messages)}")

    for _, fields in messages:
        print("Sending one message...")

        dlq_message = {
            **fields,
            "failure_reason": reason,
            "failed_at": datetime.utcnow().isoformat(),
        }

        result = await redis.xadd(
            DLQ_STREAM,
            dlq_message,
        )

        print(f"Inserted into DLQ: {result}")

    print("<<<<<<<< FINISHED DLQ FUNCTION >>>>>>>>")


# async def send_to_dlq(messages, reason):
#     print(f"\nMoving {len(messages)} messages to DLQ...\n")

#     for _, fields in messages:
#         dlq_message = {
#             **fields,
#             "failure_reason": reason,
#             "failed_at": datetime.utcnow().isoformat(),
#         }

#         await redis.xadd(
#             DLQ_STREAM,
#             dlq_message,
#         )

#     print("Messages moved to Dead Letter Queue\n")


async def process_batch(logs):
    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with get_db() as db:
                save_logs_bulk(db, logs)

            print(f"Batch stored successfully (attempt {attempt})")

            return True, None

        except Exception as e:
            last_exception = str(e)

            print(f"Attempt {attempt} failed:")
            print(last_exception)

            if attempt < MAX_RETRIES:
                print("Retrying in 2 seconds...\n")
                await asyncio.sleep(2)

    print("Batch permanently failed.\n")

    return False, last_exception


async def process_messages(messages):

    logs = []
    message_ids = []

    for message_id, fields in messages:
        logs.append(
            Log(
                service=fields["service"],
                level=fields["level"],
                message=fields["message"],
                timestamp=fields["timestamp"],
                request_id=fields["request_id"],
                user_id=fields["user_id"],
                log_metadata=json.loads(fields["metadata"]),
            )
        )

        message_ids.append(message_id)

    success, reason = await process_batch(logs)

    if success:
        await redis.xack(
            STREAM,
            GROUP,
            *message_ids,
        )

        print(f"ACKed {len(message_ids)} messages\n")

    else:
        try:
            await send_to_dlq(messages, reason)
        except Exception as e:
            print("DLQ ERROR:")
            print(repr(e))
            raise

        await redis.xack(
            STREAM,
            GROUP,
            *message_ids,
        )

        print("Failed batch moved to DLQ and ACKed.\n")


async def recover_pending():

    print("Checking pending messages...")

    while True:
        response = await redis.xautoclaim(
            STREAM,
            GROUP,
            CONSUMER,
            min_idle_time=5000,
            start_id="0-0",
            count=BATCH_SIZE,
        )

        _, messages, _ = response

        if not messages:
            break

        print(f"Recovered {len(messages)} pending messages")

        await process_messages(messages)


async def consume():

    await create_group()

    await recover_pending()

    print("Worker started\n")

    while True:
        response = await redis.xreadgroup(
            groupname=GROUP,
            consumername=CONSUMER,
            streams={STREAM: ">"},
            count=BATCH_SIZE,
            block=5000,
        )

        if not response:
            continue

        _, messages = response[0]

        await process_messages(messages)


if __name__ == "__main__":
    asyncio.run(consume())
