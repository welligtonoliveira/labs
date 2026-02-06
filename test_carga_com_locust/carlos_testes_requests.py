import requests
import json
from serpens import schema

# headers = {"Content-Type": "application/json"}


payload = {
    "name": "Well Well Wells",
    "email": "well.wells@example.com"
}


p1 = json.dumps(payload, cls=schema.SchemaEncoder)
# l_pi = json.loads(p1)


response = requests.request(method="POST",
                     url="https://webhook.site/babd1c08-d50e-46cc-9b1b-e543b0162c02",
                     data=p1)