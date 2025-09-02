import os
import csv
import json
from google.cloud import pubsub_v1

# Define o caminho da credencial JSON (assumindo que está na raiz do projeto)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sua-chave-de-servico.json"

# Parâmetros do Pub/Sub
PROJECT_ID = "seu-projeto-id"
TOPIC_ID = "nome-do-topico"
CSV_FILE = "seuarquivo.csv"

# Inicializa o publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_messages_from_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            message = json.dumps({
                "document": row["document"],
                "contract_id": row["contract_id"]
            }).encode("utf-8")

            future = publisher.publish(topic_path, message)
            print(f"Mensagem enviada: {row}, ID: {future.result()}")

if __name__ == "__main__":
    publish_messages_from_csv(CSV_FILE)
