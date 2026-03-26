import datetime
from google.cloud import pubsub_v1

PROJECT_ID = "dotz-noverde-prd"
SUBSCRIPTION_ID = "platform-servicing-subscription-send-to-conciliation-dlq"

TARGET_DATE = datetime.date(2026, 3, 26)

def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    print(f"Filtering DLQ: {subscription_path}")
    print(f"Targeting only messages from: {TARGET_DATE} (Local Time)")

    try:
        while True:
            response = subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": 100,
                }
            )

            if not response.received_messages:
                print("No  messages to process")
                break

            ack_ids = []
            for received_message in response.received_messages:
                message = received_message.message
                local_publish_time = message.publish_time.astimezone()
                message_date = local_publish_time.date()

                if message_date == TARGET_DATE:
                    data = message.data.decode("utf-8", errors="replace")
                    print(f"[MATCH] ACKing message from {message_date}: {data[:100]}")
                    ack_ids.append(received_message.ack_id)
                else:
                    print(f"[SKIP] Message from {message_date} ignored")

            if ack_ids:
                subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": ack_ids,
                    }
                )

    except KeyboardInterrupt:
        print("\nStopping pull")
    finally:
        subscriber.close()

if __name__ == "__main__":
    main()