import csv
import json
import time  # Import required for adding delays
from concurrent import futures
from google.cloud import pubsub_v1

# Define o caminho da credencial JSON (assumindo que está na raiz do projeto)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sua-chave-de-servico.json"

# Parâmetros do Pub/Sub
PROJECT_ID = "dotz-noverde-prd"
TOPIC_ID = "techfin-pix-automatic-payee-payment-schedule"
CSV_FILE = "scheduled99.csv"

# Inicializa o publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

FUNDING_DETAILS = {
    'fidc_dotzplgn':{
            'slug': 'fidc_dotzplgn',
            'bank': 'BTG Pactual',
            'bank_code': '208',
            'bank_agency': '1',
            'bank_account': '18396200'
        },
    'noverde_empirica':
        {
            'slug': 'noverde_empirica',
            'bank': 'BTG Pactual',
            'bank_code': '208',
            'bank_agency': '30',
            'bank_account': '003299492'
        },
    'fidc_dotzfin':
        {
            'slug': 'fidc_dotzfin',
            'bank': 'BTG Pactual',
            'bank_code': '208',
            'bank_agency': '30',
            'bank_account': '8542473'
        }
}

def publish_messages_from_csv(csv_file):
    batch_size = 30
    pending_messages = []

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')

        for row in reader:
            message = json.dumps({
                "recurrence_payment_id": str(row["recurrence_payment_id"]),
                "funding": str(row["funding"]),
                "funding_details": FUNDING_DETAILS.get(str(row["funding"]))
            }).encode("utf-8")

            future = publisher.publish(topic_path, message)
            pending_messages.append((row, future))
            print(f"Publicando na fila: {row['recurrence_payment_id']}")

            # Se o lote atingiu 30, processa e aguarda 5 segundos
            if len(pending_messages) >= batch_size:
                process_batch(pending_messages)
                pending_messages.clear()
                print("Lote processado. Aguardando 5 segundos para o próximo lote...\n")
                time.sleep(5)

        # Processa qualquer mensagem restante no final do arquivo
        if pending_messages:
            process_batch(pending_messages)

def process_batch(pending_messages):
    print(f"Aguardando confirmação de {len(pending_messages)} mensagens...")
    futures_list = [future for _, future in pending_messages]

    futures.wait(futures_list, return_when=futures.ALL_COMPLETED)

    for row, future in pending_messages:
        # future.result() will return the message ID or throw an exception if it failed
        print(f"Mensagem confirmada: {row['recurrence_payment_id']}, ID: {future.result()}")

if __name__ == "__main__":
    publish_messages_from_csv(CSV_FILE)