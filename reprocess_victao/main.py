import csv
import json
from uuid import uuid4


def read_csv(file_path):

    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            payload = {}
            payload["loan_id"] = row["loan_id"]
            payload["ccb_number"] = row["ccb_number"]
            payload["bank_name"] = row["bank_name"]
            payload["cnab_filename"] = row["cnab_filename"]
            payload["status"] = row["status"]
            payload["updated_at"] = row["updated_at"]
            message_content = {"Id": str(uuid4())}
            message_content["MessageBody"] = json.dumps(payload)
            data.append(message_content)
    return data

def write_json(data, base_filename, max_lines=10):
    total_files = (len(data) + max_lines - 1) // max_lines
    for i in range(total_files):
        start_index = i * max_lines
        end_index = start_index + max_lines
        chunk = data[start_index:end_index]
        file_name = f"{base_filename}_part_{i + 1}.json"
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(chunk, file)
        print(f"Arquivo JSON gerado: {file_name}")

def main():
    csv_file = 'Conciliation_2025-08-07.csv'
    base_filename = './output/analyses'

    data = read_csv(csv_file)
    write_json(data, base_filename)

if __name__ == "__main__":
    main()