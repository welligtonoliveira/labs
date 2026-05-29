from locust import HttpUser, task, between
import random
import json
from datetime import datetime, timedelta

# List of first names, middle names and last names to generate realistic Brazilian names
FIRST_NAMES = [
    "Tiago", "Felipe", "Lucas", "Mateus", "Gabriel", "Bruno", "Rodrigo", "Diego", "Rafael", "Gustavo",
    "Juliana", "Mariana", "Aline", "Camila", "Larissa", "Amanda", "Beatriz", "Letícia", "Bruna", "Fernanda",
    "Arthur", "Bernardo", "Heitor", "Enzo", "Lorenzo", "Theo", "Pedro", "Benjamin", "Miguel", "Davi",
    "Ana", "Maria", "João", "Pedro", "Carlos", "José", "Marcos", "Paulo", "Luiz", "Fernando"
]

MIDDLE_NAMES = [
    "Felipe", "Lucas", "Santos", "Oliveira", "Silva", "Souza", "Lima", "Pereira", "Alves", "Costa",
    "Gomes", "Martins", "Araújo", "Rodrigues", "Nascimento", "Ribeiro", "Carvalho", "Melo", "Cardoso", "Teixeira"
]

LAST_NAMES = [
    "Santos", "Oliveira", "Silva", "Souza", "Lima", "Pereira", "Alves", "Costa",
    "Gomes", "Martins", "Araújo", "Rodrigues", "Nascimento", "Ribeiro", "Carvalho", "Melo", "Cardoso", "Teixeira"
]

# Valid area codes (DDDs) in Brazil
DDDS = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "21", "22", "24", "27", "28", "31", "32", "33", "34", "35", "37", "38", "41", "42", "43", "44", "45", "46", "47", "48", "49", "51", "53", "54", "55", "61", "62", "63", "64", "65", "66", "67", "68", "69", "71", "73", "74", "75", "77", "79", "81", "82", "83", "84", "85", "86", "87", "88", "89", "91", "92", "93", "94", "95", "96", "97", "98", "99"]

def generate_cpf():
    """Generates a mathematically valid, random Brazilian CPF (only digits)."""
    base = [random.randint(0, 9) for _ in range(9)]
    
    # Calculate first verifier digit (multipliers 10 to 2)
    s = sum((10 - i) * base[i] for i in range(9))
    d1 = 0 if s % 11 < 2 else 11 - (s % 11)
    
    # Calculate second verifier digit (multipliers 11 to 2)
    base.append(d1)
    s = sum((11 - i) * base[i] for i in range(10))
    d2 = 0 if s % 11 < 2 else 11 - (s % 11)
    
    base.append(d2)
    return "".join(map(str, base))


def generate_name():
    """Generates a random full name with realistic Brazilian parts."""
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    
    while middle == first:
        middle = random.choice(MIDDLE_NAMES)
    while last == middle or last == first:
        last = random.choice(LAST_NAMES)
        
    return f"{first} {middle} {last}"

def generate_birthdate():
    """Generates a random birthdate for a person between 18 and 65 years old in YYYY-MM-DD format."""
    start_date = datetime.now() - timedelta(days=65*365)
    end_date = datetime.now() - timedelta(days=18*365)
    random_days = random.randint(0, (end_date - start_date).days)
    birth_date = start_date + timedelta(days=random_days)
    return birth_date.strftime("%Y-%m-%d")

def generate_email(name):
    """Generates a valid, clean ASCII-only email based on the generated name."""
    import unicodedata
    # Normalize unicode to decomposed form and encode to ASCII to drop accent marks
    normalized = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    clean_name = normalized.lower().replace(" ", ".")
    # Strip out non-alphanumeric/non-dot characters
    clean_name = "".join(c for c in clean_name if c.isalnum() or c == ".")
    domain = random.choice(["gmail.com", "yahoo.com.br", "hotmail.com", "outlook.com", "dotz.com"])
    return f"{clean_name}@{domain}"


def generate_mobile_number():
    """Generates a random valid Brazilian mobile number (11 digits: DDD + 9 + 8 digits)."""
    ddd = random.choice(DDDS)
    suffix = "".join(random.choice("0123456789") for _ in range(8))
    return f"{ddd}9{suffix}"

class LoanStressTestUser(HttpUser):
    wait_time = between(1, 3) # Wait between 1 and 3 seconds between task loops
    
    # Base URL for the target API service
    host = "https://api.stg.noverde.com.br"
    
    @task
    def execute_loan_flow(self):
        # 1. Create a dynamic and realistic loan application payload
        name = generate_name()
        payload = {
            "document": generate_cpf(),
            "name": name,
            "birthdate": generate_birthdate(),
            "email": generate_email(name),
            "mobile_number": generate_mobile_number(),
            "income": 15000,
            "employment_status": "employee",
            "requested_amount": 500,
            "requested_period": 12,
            "requested_payday": 10,
            "request_installment": 200,
            "reason": "travel",
            "address": {
                "zipcode": "02069-060",
                "street_name": "Rua Nabi Mansur Sadek",
                "building_number": "329",
                "neighborhood": "Carandiru",
                "city": "São Paulo",
                "state": "SP"
            },
            "fingerprint": {
                "device_info": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1"
            },
            "bank_account": {
                "bank_code": "341",
                "agency": "0247",
                "account": "51354",
                "account_digit": "5",
                "account_type": "savings"
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "a267b223-c52f-4d35-8f8a-33d28577a4f7"
        }
        
        loan_id = None
        
        # 2. POST - Create the loan application
        with self.client.post(
            "/v1/loans",
            json=payload,
            headers=headers,
            name="POST /v1/loans",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    loan_id = response_data.get("uid")
                    if loan_id:
                        response.success()
                    else:
                        response.failure("Response was successful but missing 'uid' field")
                except json.JSONDecodeError:
                    response.failure("Failed to parse JSON response body")
            else:
                response.failure(f"Loan creation failed with status {response.status_code}: {response.text}")
                
        # 3. PUT - Request Credit Analysis (only if loan creation succeeded and we got a loan_id)
        if loan_id:
            # We send an empty body as per specification: --data ''
            with self.client.put(
                f"/v1/loans/{loan_id}/credit-analysis",
                data="",
                headers=headers,
                name="PUT /v1/loans/{loan_id}/credit-analysis",
                catch_response=True
            ) as response:
                if response.status_code in [200, 201, 202, 204]:
                    response.success()
                else:
                    response.failure(f"Credit analysis failed with status {response.status_code}: {response.text}")
