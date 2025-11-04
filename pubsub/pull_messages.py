
from google.cloud import pubsub_v1

# Set these values
PROJECT_ID = "dotz-noverde-prd"
SUBSCRIPTION_ID = "platform-customers-release-contracts-queue-dlq-sub"

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    try:
        data = message.data.decode("utf-8")
        print(data)
    except Exception:
        print(message.data)
    
    message.ack()

def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    print(f"Listening to DLQ subscription: {subscription_path}")
    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)

    try:
        streaming_pull.result()  # Blocks and listens indefinitely
    except KeyboardInterrupt:
        streaming_pull.cancel()
        print("\nStopped.")

if __name__ == "__main__":
    main()
