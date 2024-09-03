import csv
import json
import os
from uuid import uuid4


def read_csv(file_path):
    """Lê o arquivo CSV e retorna uma lista de dicionários."""
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["occurrence_code"] = 110
            row["loan_id"] = int(row["loan_id"])
            row["installment_id"] = int(row["installment_id"])
            row["paid_value"] = float(row["paid_value"])
            message_content = {"Id": str(uuid4())}
            message_content["MessageBody"] = json.dumps(row)
            data.append(message_content)
    return data

def write_json(data, base_filename, max_lines=10):
    """Escreve os dados em arquivos JSON com no máximo `max_lines` linhas cada."""
    total_files = (len(data) + max_lines - 1) // max_lines  # Calcula o número de arquivos necessários
    for i in range(total_files):
        start_index = i * max_lines
        end_index = start_index + max_lines
        chunk = data[start_index:end_index]
        file_name = f"{base_filename}_part_{i + 1}.json"
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(chunk, file)
        print(f"Arquivo JSON gerado: {file_name}")

def main():
    csv_file = './input/20240808-20240812.csv'  # Substitua pelo caminho do seu arquivo CSV
    base_filename = './output/out_20240808-20240812'  # Nome base para os arquivos JSON

    data = read_csv(csv_file)
    write_json(data, base_filename)

if __name__ == "__main__":
    main()
