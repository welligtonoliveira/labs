from locust import HttpUser, TaskSet, task, between
import random

def generate_cpf():
    """Gera um CPF aleatório."""
    def calculate_digit(digits):
        s = sum((10 - i) * int(d) for i, d in enumerate(digits))
        return 0 if s % 11 < 2 else 11 - (s % 11)

    base = [random.randint(0, 9) for _ in range(9)]
    d1 = calculate_digit(base)
    d2 = calculate_digit(base + [d1])
    return f"{''.join(map(str, base))}{d1}{d2}"

class UserBehavior(TaskSet):
    
    @task
    def send_request(self):
        cpf = generate_cpf()
        payload = {
            "name": "Well Well Wells",
            "email": "70729229890@gmail.com",
            "document": cpf,
            "birthdate": "1985-01-23",
            "requested_amount": 5671.43,
            "requested_period": 15,
            "requested_payday": 20,
            "callback": {
                "url": "https://68de-189-37-66-231.ngrok-free.app",
                "authorization": "9a0307f3-d433-4357-869c-29fdb3d958bb"
            },
            "monthly_income": 3462,
            "address": {
                "zipcode": "69911484",
                "street_name": "Travessa Messias",
                "building_number": "336",
                "neighborhood": "João Eduardo II",
                "city": "Rio Branco",
                "state": "SP"
            },
            "fingerprint": {
                "ip": "191.9.113.61",
                "apigateway": {
                    "source_ip": "44.206.6.50",
                    "user_agent": "GuzzleHttp/7"
                },
                "device_info": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "geolocation": None
            }
        }
        
        self.client.post(
            '/credit-analysis',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': 'TdApwFbTujqyujpiDgPkkkzyTkUYuAQtiCQcSLAV'
            },
            proxies={"http": "socks5h://localhost:9999", "https": "socks5h://localhost:9999"}
        )

class WebsiteUser(HttpUser):
    host = "https://risk.internal.api.stg.noverde.net"
    tasks = [UserBehavior]
    wait_time = between(1, 3)
