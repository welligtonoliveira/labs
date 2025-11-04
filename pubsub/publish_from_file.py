import json
import time
from pathlib import Path

from google.cloud import pubsub_v1

# === CONFIGURATION ===
PROJECT_ID = "dotz-noverde-prd"
TOPIC_ID = "platform-customers-release-contracts-queue"
FILE_PATH = "messages.txt"
PUBLISHED_LOG = "published.log"
SLEEP_SECONDS = 0.2  # delay between publishes (in seconds)


def load_published_ids(log_path: str):
    """Load previously published message IDs (if file exists)."""
    if not Path(log_path).exists():
        return set()
    with open(log_path, "r") as f:
        return {line.strip() for line in f if line.strip()}


def append_published_id(log_path: str, message_id: str):
    """Append a message ID to the log file."""
    with open(log_path, "a") as f:
        f.write(message_id + "\n")


def publish_messages(project_id: str, topic_id: str, file_path: str, log_path: str, delay: float):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    published_ids = load_published_ids(log_path)
    print(f"Loaded {len(published_ids)} previously published message IDs.")

    with open(file_path, "r") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                # Check if this message has already been published
                msg_hash = str(hash(line))
                if msg_hash in published_ids:
                    print(f"Skipping line {line_number} (already published).")
                    continue

                # Publish message
                data = json.loads(line)
                message_data = json.dumps(data).encode("utf-8")
                future = publisher.publish(topic_path, message_data)
                message_id = future.result()  # wait for server ack

                append_published_id(log_path, msg_hash)
                published_ids.add(msg_hash)

                print(f"✅ Published line {line_number}: {data} (ID: {message_id})")

                # Sleep delay
                time.sleep(delay)

            except json.JSONDecodeError:
                print(f"⚠️  Invalid JSON at line {line_number}: {line}")
            except Exception as e:
                print(f"❌ Error publishing line {line_number}: {e}")


if __name__ == "__main__":
    publish_messages(PROJECT_ID, TOPIC_ID, FILE_PATH, PUBLISHED_LOG, SLEEP_SECONDS)
