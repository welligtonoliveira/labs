import csv
from datetime import datetime, date, timedelta

# from google.cloud import pubsub_v1

# Define o caminho da credencial JSON (assumindo que está na raiz do projeto)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sua-chave-de-servico.json"

# Parâmetros do Pub/Sub
# PROJECT_ID = "dotz-noverde-prd"
# TOPIC_ID = "platform-servicing-topic-restore-credit-queue"
CSV_FILE = "RESTORE_CREDIT_QUEUE - BNPL.csv"

# Inicializa o publisher
# publisher = pubsub_v1.PublisherClient()
# topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_messages_from_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        total = 0
        for i, row in enumerate(reader, start=1):
            now = date.today()
            data = datetime.fromisoformat(row["receivable_processed_at"]).date()
            one_day_ago = now - timedelta(days=1)
            if data > now or data < one_day_ago:
                continue
            # message = json.dumps({
            #     "receivable_processed_at": row["receivable_processed_at"],
            #     "loan_uuid": row["loan_uuid"],
            #     "paid_installments_quantity": int(row["paid_installments_quantity"]),
            #     "reason": "Baixa de pagamento processada"
            # }).encode("utf-8")

            # future = publisher.publish(topic_path, message)
            print(f"{row['loan_uuid']}")
            total += 1

        print(f"Publicação finalizada! Total: {total}")

if __name__ == "__main__":
    publish_messages_from_csv(CSV_FILE)
