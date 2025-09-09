import csv
import json

# from google.cloud import pubsub_v1

# Define o caminho da credencial JSON (assumindo que está na raiz do projeto)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sua-chave-de-servico.json"

# Parâmetros do Pub/Sub
PROJECT_ID = "dotz-noverde-prd"
TOPIC_ID = "platform-payments-cancel-by-id"
CSV_FILE = "payments_to_cancel.csv"

# Inicializa o publisher
# publisher = pubsub_v1.PublisherClient()
# topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_messages_from_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            message = json.dumps({
                "payment_id": row["ID"],
                "cancel_reason": "payment without expense",
                "referrer": "/event/cancel-by-id-queue"
            }).encode("utf-8")

            print(message)
            # future = publisher.publish(topic_path, message)
            # print(f"Mensagem enviada: Payment_id {row['ID']}, ID: {future.result()}")

if __name__ == "__main__":
    publish_messages_from_csv(CSV_FILE)
