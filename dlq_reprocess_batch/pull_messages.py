import sys
from google.cloud import pubsub_v1

# Set these values
PROJECT_ID = "dotz-noverde-prd"
SUBSCRIPTION_ID = "integrator-vcom-subscription-new-debt-dlq"

def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    print(f"Peeking at messages from DLQ: {subscription_path}", file=sys.stderr)
    
    seen_message_ids = set()
    total_messages_saved = 0

    while True:
        response = subscriber.pull(
            request={
                "subscription": subscription_path,
                "max_messages": 100, 
            }
        )

        if not response.received_messages:
            print("\nNo more messages found right now. Exiting.", file=sys.stderr)
            break
            
        new_messages_in_batch = 0

        for received_message in response.received_messages:
            message = received_message.message
            
            # Prevent duplicates and infinite loops if unacked messages reappear
            if message.message_id in seen_message_ids:
                continue
                
            seen_message_ids.add(message.message_id)
            new_messages_in_batch += 1
            
            try:
                data = message.data.decode("utf-8")
                print(data)
            except Exception:
                print(message.data.decode("utf-8", errors="replace"))

        # If we only pulled messages we've already seen, we've looped through the whole queue
        if new_messages_in_batch == 0:
            print("\nOnly duplicate messages received. We have seen the whole queue. Exiting.", file=sys.stderr)
            break

        total_messages_saved += new_messages_in_batch
        print(f"Saved a batch of {new_messages_in_batch} unique messages...", file=sys.stderr)

    print(f"Finished. Total unique messages saved (NOT acknowledged): {total_messages_saved}", file=sys.stderr)

if __name__ == "__main__":
    main()