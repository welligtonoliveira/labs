# context

- Desenvolver um job capaz de realizar testes de stress atraves de requests de apis.

# requisitos

- Ter report com todos os status e situações


# arquitetura

- Utilizar locust

# dados

- o job deve ser capaz de realizar requisições para o dois endpoints abaixo onde o segunda tem dependencia com a resposta do primeiro.

    1 - POST-  curl --location 'https://api.stg.noverde.com.br/v1/loans' \
--header 'Content-Type: application/json' \
--header 'Authorization: a267b223-c52f-4d35-8f8a-33d28577a4f7' \
--data-raw '{
    "document": "88377452308",
    "name": "Tiago Felipe Lucas Santos",
    "birthdate": "1988-01-23",
    "email": "welligton.oliveira@dotz.com",
    "mobile_number": "35999916880",
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
}'

    2 - PUT - curl --location --request PUT 'https://api.stg.noverde.com.br/v1/loans/ad9e3621-07d5-4a38-8082-4783d3ba50ac/credit-analysis' \
--header 'Content-Type: application/json' \
--header 'Authorization: a267b223-c52f-4d35-8f8a-33d28577a4f7' \
--data ''

# regras
 - na request 1 os valores dos atributos document, name, birthdate, email e mobile_number devem ser aleatórios, porem, com formatacao valida.
 - na request 2 o valor do atributo loan_id deve ser captura da response da request 1, segue exemplo de response:
{
    "uid": "ad9e3621-07d5-4a38-8082-4783d3ba50ac"
}
 - criar um readme.md do projeto com orientacoes para uso.
 - toda estrutura deve ser em python e ficar dentro da pasta test_stress_loans/

# libs
- as libs usadas devem precisam estar no requirements.txt


