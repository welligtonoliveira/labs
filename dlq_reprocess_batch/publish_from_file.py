import json
import sys
import time
import hashlib
from pathlib import Path
from concurrent import futures

from google.cloud import pubsub_v1

# === CONFIGURATION ===
PROJECT_ID = "dotz-noverde-prd"
TOPIC_ID = "integrator-vcom-topic-new-debt-queue"
FILE_PATH = "messages.txt"
PUBLISHED_LOG = "published.log"
BATCH_SIZE = 10
SLEEP_SECONDS = 15  # delay between batches


def load_published_ids(log_path: str) -> set:
    """Load previously published stable message hashes."""
    if not Path(log_path).exists():
        return set()
    with open(log_path, "r") as f:
        return {line.strip() for line in f if line.strip()}


def get_stable_hash(text: str) -> str:
    """Generate a stable SHA-256 hash that persists across script restarts."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def process_batch(pending_messages: list, f_log, published_ids: set):
    """Waits for the batch to complete, logs successes, and clears the list."""
    print(f"Aguardando confirmação de {len(pending_messages)} mensagens...")
    
    # Extract just the future objects for the waiter
    futures_list = [item["future"] for item in pending_messages]
    futures.wait(futures_list, return_when=futures.ALL_COMPLETED)

    for item in pending_messages:
        try:
            # .result() returns the message ID or throws an exception if it failed
            message_id = item["future"].result()
            
            # Log the success safely AFTER confirmation
            f_log.write(item["hash"] + "\n")
            published_ids.add(item["hash"])
            print(f"✅ Mensagem confirmada: linha {item['line_number']} (ID: {message_id})")
            
        except Exception as e:
            print(f"❌ Error publishing line {item['line_number']}: {e}")
            
    # Force write to disk once per batch for efficiency
    f_log.flush()
    pending_messages.clear()


def publish_messages(project_id: str, topic_id: str, file_path: str, log_path: str, batch_size: int, delay: float):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    published_ids = load_published_ids(log_path)
    print(f"Loaded {len(published_ids)} previously published message IDs.")

    pending_messages = []

    # Open both files at once
    with open(file_path, "r") as f_in, open(log_path, "a") as f_log:
        for line_number, line in enumerate(f_in, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                # 1. Deduplication using stable hash
                msg_hash = get_stable_hash(line)
                if msg_hash in published_ids:
                    print(f"Skipping line {line_number} (already published).", file=sys.stderr)
                    continue

                # 2. Validate JSON
                data = json.loads(line)
                message_data = json.dumps(data).encode("utf-8")
                
                # 3. Publish to Pub/Sub asynchronously
                future = publisher.publish(topic_path, message_data)
                
                # Append a dictionary to track metadata alongside the future
                pending_messages.append({
                    "line_number": line_number,
                    "hash": msg_hash,
                    "future": future
                })
                print(f"Publicando na fila: linha {line_number}")

                # 4. Process Batch if it reaches the size limit
                if len(pending_messages) >= batch_size:
                    process_batch(pending_messages, f_log, published_ids)
                    print(f"Lote processado. Aguardando {delay} segundos para o próximo lote...\n", file=sys.stderr)
                    time.sleep(delay)

            except json.JSONDecodeError:
                print(f"⚠️  Invalid JSON at line {line_number}: {line}")
            except Exception as e:
                print(f"❌ Error preparing line {line_number}: {e}")

        # 5. Process any remaining messages at the end of the file
        if pending_messages:
            process_batch(pending_messages, f_log, published_ids)
            print("Lote final processado.\n")


if __name__ == "__main__":
    publish_messages(PROJECT_ID, TOPIC_ID, FILE_PATH, PUBLISHED_LOG, BATCH_SIZE, SLEEP_SECONDS)