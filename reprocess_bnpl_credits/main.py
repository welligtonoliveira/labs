import csv
import json
import time

from google.cloud import pubsub_v1

# Define o caminho da credencial JSON (assumindo que está na raiz do projeto)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sua-chave-de-servico.json"

# Parâmetros do Pub/Sub
PROJECT_ID = "dotz-noverde-prd"
TOPIC_ID = "techfin-pix-automatic-payee-payment-batch-cancellation"
CSV_FILE = "reprocess_cancellation_recurrence_payments.csv"

# Inicializa o publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_messages_from_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for i, row in enumerate(reader, start=1):
            message = json.dumps({
                "recurrence_id": row["recurrence_id"]
            }).encode("utf-8")
            # message = json.dumps({
            #     "receivable_processed_at": row["receivable_processed_at"],
            #     "loan_uuid": row["loan_uuid"],
            #     "paid_installments_quantity": int(row["paid_installments_quantity"]),
            #     "reason": "Baixa de pagamento processada"
            # }).encode("utf-8")

            # message = json.dumps({
            #     "document": row["document"],
            #     "reason": "Baixa de pagamento processada"
            # }).encode("utf-8")

            future = publisher.publish(topic_path, message)
            print(f"Mensagem enviada: recurrence_id {row['recurrence_id']}, ID: {future.result()}")

            if i % 100 == 0:
                print(f"{i} mensagens enviadas, pausando 2s...")
                time.sleep(2)

        print(f"Publicação finalizada! Total de mensagens enviadas: {i}")

if __name__ == "__main__":
    publish_messages_from_csv(CSV_FILE)
