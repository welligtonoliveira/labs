import unittest
import json
import os
from io import StringIO
from process import read_csv, write_json  # Substitua 'script' pelo nome do seu arquivo Python principal

class TestCSVtoJSON(unittest.TestCase):
    
    def setUp(self):
        self.csv_data = """document,loan_id,loan_uuid,installment_id,motivation,payment_date,paid_value
70869855034,19585549,53cc5f68-c0ba-4d18-9d68-35bb9fddd805,3755880,troca_com_troco,2024-08-11,439.72
12345678901,98765432,123e4567-e89b-12d3-a456-426614174001,1234567,pagamento_completo,2024-08-12,550.00
"""
        self.expected_data = [
            {"document": "70869855034", "loan_id": "19585549", "loan_uuid": "53cc5f68-c0ba-4d18-9d68-35bb9fddd805", "installment_id": "3755880", "motivation": "troca_com_troco", "payment_date": "2024-08-11", "paid_value": "439.72"},
            {"document": "12345678901", "loan_id": "98765432", "loan_uuid": "123e4567-e89b-12d3-a456-426614174001", "installment_id": "1234567", "motivation": "pagamento_completo", "payment_date": "2024-08-12", "paid_value": "550.00"}
        ]
    
    def test_read_csv(self):
        file_stream = StringIO(self.csv_data)
        result = read_csv(file_stream.getvalue())
        self.assertEqual(result, self.expected_data)
    
    def test_write_json(self):
        # Testa a criação de arquivos JSON
        file_names = write_json(self.expected_data, 'test_json')
        for file_name in file_names:
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.assertIsInstance(data, list)
                self.assertTrue(len(data) <= 10)  # Verifica se o arquivo contém no máximo 10 linhas
            os.remove(file_name)  # Remove o arquivo após o teste

if __name__ == '__main__':
    unittest.main()
