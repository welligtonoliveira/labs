import csv
import json
import time

from google.cloud import pubsub_v1

# Define o caminho da credencial JSON (assumindo que está na raiz do projeto)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sua-chave-de-servico.json"

# Parâmetros do Pub/Sub
PROJECT_ID = "dotz-noverde-prd"
TOPIC_ID = "platform-loans-topic-send-special-offer-to-credit-analysis-queue"
CSV_FILE = "special_export.csv"

# Inicializa o publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_messages_from_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for i, row in enumerate(reader, start=1):
            message = json.dumps({
                "special_offer_id": row["id"]
            }).encode("utf-8")

            future = publisher.publish(topic_path, message)
            print(f"Mensagem enviada: special_offer_id {row['id']}, ID: {future.result()}")

            if i % 100 == 0:
                print(f"{i} mensagens enviadas, pausando 2s...")
                time.sleep(2)

        print(f"Publicação finalizada! Total de mensagens enviadas: {i}")

if __name__ == "__main__":
    publish_messages_from_csv(CSV_FILE)
