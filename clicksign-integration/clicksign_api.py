from uuid import UUID
import requests
import logging
import settings

def clicksign_request(method: str, path: str, **kwargs) -> dict:
    url = settings.clicksign_url + path
    params = {'access_token': settings.access_token}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    try:
        response = requests.request(method, url=url, headers=headers, params=params, **kwargs)
    except requests.RequestException as error:
        msg = f"Unexpected request error: url {url}, message {str(error)}"
        logging.error(msg)
        return None

    return response

def create_document(data: dict) -> str:
    path = f"/v1/templates/{settings.model_key}/documents"

    loan_id = data["loan_id"]
    lecca_id = data["lecca_id"]

    document_path = settings.clicksign_document_path

    payload = {
      "document": {
        "path": f"{document_path}/contrato-{lecca_id}.docx",
        "template": {
          "data": data
        }
      }
    }

    response = clicksign_request(method="post", path=path, json=payload)

    if response is None:
        msg = f"create_document error loan_id {loan_id}, payload {payload}: check previous error"
        logging.error(msg)
        return None

    if response.status_code != 201:
        msg = f"create_document error loan_id {loan_id}: status_code {response.status_code}, response {response.text}"
        logging.error(msg)
        return None

    return response.json()["document"]["key"]
  
def add_signatary(signer_key: str, document_key: UUID) -> int:
    path = "/v1/lists"

    payload = {
        "list": {
            "document_key": document_key,
            "signer_key": signer_key,
            "sign_as": "sign",
            "message": "",
        }
    }

    response = clicksign_request(method="post", path=path, json=payload)

    if response is None:
        return False

    if response.status_code != 201:
        msg = f"add_signatary error: status_code {response.status_code}, response {response.text}"
        logging.error(msg)
        return False

    return True
  
def create_batch(signer_key: str, documents_keys: list) -> str:
    path = "/v1/batches"

    payload = {
        "batch": {
            "signer_key": signer_key,
            "document_keys": documents_keys,
            "summary": True,
        }
    }

    response = clicksign_request(method="post", path=path, json=payload)

    if response is None:
        return None

    if response.status_code != 201:
        msg = f"create_batch error: status_code {response.status_code}, response {response.text}"
        logging.error(msg)
        return None

    return response.json()["batch"]["request_signature_key"]

def notification(request_signature_key: UUID, message: str) -> int:
    path = "/v1/notifications"

    payload = {
        "request_signature_key": request_signature_key,
        "message": message,
    }

    response = clicksign_request(method="post", path=path, json=payload)

    if response is None:
        return False

    if response.status_code != 202:
        msg = f"notification error: status_code {response.status_code}, response {response.text}"
        logging.error(msg)
        return False

    return True

def cancel_document(document_key: str) -> str:
    path = f"/v1/documents/{document_key}/cancel"

    response = clicksign_request(method="patch", path=path)

    if response is None:
        return False

    if response.status_code != 200:
        msg = f"cancel_document error: status_code {response.status_code}, response {response.text}"
        logging.error(msg)
        return False

    return True
