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
            payload["api_key"] = row["api_key"]
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
    csv_file = 'SettledLoansservicing2025-09-08_1654.csv'
    base_filename = './output/analyses_parent_2025_09_08_1654'

    data = read_csv(csv_file)
    write_json(data, base_filename)

if __name__ == "__main__":
    main()