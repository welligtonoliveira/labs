#!/usr/bin/env python3
"""
End-to-end loan flow driver: create → LENT.

Walks the loan state machine through every step, driven entirely through the
Noverde EP **partner** API — Authorization: <partner api_key> on every call,
no borrower login/signup involved. Endpoints and payload shapes come from the
"Partner Loan Collection" Postman collection.

Partner path (PARTNER_API_KEY, BASE_URL):
  1. POST  /v1/loans                                     → loan (current_state=SIMULATION)
  2. PATCH /v1/loans/{uid}                                → attach RG/gender/marital status/mother's name
  3. PUT   /v1/loans/{uid}/credit-analysis               → WAITING_CREDIT_ANALYSIS
  4. (poll)                                              ← real risk system callback → PROPOSAL
  5. PUT   /v1/loans/{uid}/offers                        → PENDING
  6. POST  /v1/loans/{uid}/bank-accounts  (Banco do Brasil account/agency)
  7. POST  /v1/loans/{uid}/attachments  (selfie)
  8. POST  /v1/loans/{uid}/attachments  (document_front)
  9. POST  /v1/loans/{uid}/attachments  (life_proof)
 10. PUT   /v1/loans/{uid}/agreements                    → CCB created
 11. PUT   /v1/loans/{uid}/application                   → WAITING_FRAUD_ANALYSIS
 12. POST  /v1/loans/fraud-analysis/callback (private)   → WAITING_FUNDING
 13. (poll)                                              ← disbursal now runs automatically → LENT
 14. GET   /v1/loans/{uid}                               → assert current_state == lent

Borrower identity (CPF/name/RG/mother's name/birthdate/mobile/address) and
the bank account used to receive the loan are both generated fresh from
4devs.com.br on every run (see generate_fake_borrower and
generate_fake_bank_account), since the platform rejects a second loan
application for the same CPF. Email uses the itest+<n>@noverde.tests.io
convention instead, matching how the Partner Loan Collection sets up its own
test data. Set the corresponding env var below to pin any of these to a
specific value instead.

Environment variables (all optional):

  BASE_URL                 public API base  (default: https://api.stg.noverde.com.br)
  PRIVATE_BASE_URL         private API base (default: https://private.api.uat.noverde.com/platform-loans-private-api)
  PARTNER_API_KEY          Noverde EP partner api_key, sent as a raw Authorization
                            header on both the public /v1/loans endpoints and the
                            private fraud-analysis callback
  BORROWER_NAME             name sent to /v1/loans                    (default: generated via 4devs)
  BORROWER_INCOME           monthly income sent to /v1/loans          (default: 3000)
  BORROWER_BIRTHDATE        yyyy-mm-dd                                (default: generated via 4devs)
  BORROWER_EMAIL            borrower email                            (default: itest+<random>@noverde.tests.io)
  BORROWER_MOBILE           11-digit mobile w/ area code              (default: generated via 4devs)
  BORROWER_EMPLOYMENT       employment_status enum value              (default: employee)
  BORROWER_MARITAL_STATUS   marital_status enum value                 (default: single)
  REQUESTED_AMOUNT          loan amount                               (default: 500.00)
  REQUESTED_PERIOD          installment count                         (default: 8)
  REQUEST_INSTALLMENT       requested installment amount              (default: requested_amount / requested_period)
  REQUESTED_PAYDAY          payment day-of-month                      (default: 5)
  LOAN_REASON               free-text reason                          (default: travel)
  ADDRESS_ZIPCODE           zipcode                                   (default: 01010-000)
  ADDRESS_*                 street / number / neighborhood / city / state (default: generated via 4devs)
  SELFIE_B64                base64 selfie image
  DOCUMENT_FRONT_B64        base64 document front image
  LIFE_PROOF_B64            base64 life proof image
  POLL_INTERVAL             seconds between GET /loans/{uid} polls (default 3)
  POLL_TIMEOUT              total seconds to wait per state transition (default 120)
  CREDIT_ANALYSIS_TIMEOUT   seconds to wait for risk system callback (default 120)

Usage:
  python3 main.py
  BASE_URL=https://api.dev.noverde.com.br python3 main.py

The script is idempotent only at the simulation step; running it end-to-end
creates real records in the target environment. DO NOT point at production.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import time
from datetime import datetime
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Defaults pulled from the Insomnia "staging" sub-env.
DEFAULTS = {
    "BASE_URL": "https://api.stg.noverde.com.br",
    "PRIVATE_BASE_URL": "https://private.api.uat.noverde.com/platform-loans-private-api",
    "PARTNER_API_KEY": "9a0307f3-d433-4357-869c-29fdb3d958bb",
    "BORROWER_INCOME": "8000",
    "POLL_INTERVAL": "3",
    "POLL_TIMEOUT": "120",
    "CREDIT_ANALYSIS_TIMEOUT": "120",
}

# Unofficial AJAX endpoint behind https://www.4devs.com.br/gerador_de_pessoas,
# used to mint a fresh, valid-format Brazilian identity for every run.
FOUR_DEVS_URL = "https://www.4devs.com.br/ferramentas_online.php"

GENDER_CODE = {"Masculino": "M", "Feminino": "F"}

# 4devs' own numeric codes for its bank-account-format dropdown (distinct
# from real FEBRABAN bank codes). 2 = Banco do Brasil.
FOUR_DEVS_BANK_OPTION = "2"
BANCO_DO_BRASIL_CODE = "001"
BANCO_DO_BRASIL_NAME = "BANCO DO BRASIL S.A."

# 1×1 placeholder JPEG. Override with real base64 via env vars for backends that
# validate image content.
PLACEHOLDER_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsND"
    "hIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFB"
    "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQA"
    "BAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAA"
    "AP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKpgB//Z"
)


def cfg(key: str) -> str:
    val = os.environ.get(key, DEFAULTS.get(key, ""))
    if val == "":
        sys.exit(f"missing required env var: {key}")
    return val


def make_session() -> requests.Session:
    """A requests.Session that retries idempotent calls and transient errors.

    POST is intentionally included in allowed_methods because the loan-flow
    endpoints are safe to retry: each one either creates a record we'll reuse
    or returns a deterministic state transition. Real failures still surface
    via raise_for() since retry only applies to 5xx/connection-level errors.
    """
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.5,
        status_forcelist=(502, 503, 504),
        allowed_methods=("GET", "POST", "PUT", "PATCH"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=1, pool_maxsize=1)
    s = requests.Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


SESSION = make_session()

import urllib3

# Suppressed unconditionally: generate_fake_borrower() always skips cert
# verification for the 4devs call (see below), regardless of VERIFY_SSL.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if os.environ.get("VERIFY_SSL", "true").lower() in ("0", "false", "no"):
    SESSION.verify = False


def banner(step: str, title: str) -> None:
    print(f"\n--- {step}  {title} ---", flush=True)


def show(resp: requests.Response) -> None:
    print(f"  {resp.request.method} {resp.url}  →  {resp.status_code}")
    body = resp.text or ""
    print(f"  body: {body[:400]}{'…' if len(body) > 400 else ''}")


def raise_for(resp: requests.Response, step: str) -> None:
    if resp.status_code >= 400:
        sys.exit(f"step {step} failed with {resp.status_code}: {resp.text}")


def partner_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }


def private_headers(api_key: str) -> dict[str, str]:
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }


def generate_fake_borrower() -> dict[str, Any]:
    """Fetch a fresh, valid-format Brazilian identity from 4devs.com.br.

    Every run needs its own CPF: the platform rejects a second loan
    application for a CPF that already has one on file.
    """
    banner("00", "generate borrower identity (4devs)")
    resp = SESSION.post(
        FOUR_DEVS_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.4devs.com.br",
            "Referer": "https://www.4devs.com.br/gerador_de_pessoas",
            "X-Requested-With": "XMLHttpRequest",
        },
        data={
            "acao": "gerar_pessoa",
            "sexo": "I",
            "pontuacao": "S",
            "idade": random.randint(21, 60),
            "cep_estado": "",
            "txt_qtde": 1,
            "cep_cidade": "",
        },
        timeout=30,
        # Independent of VERIFY_SSL/SESSION.verify: a corporate VPN's TLS
        # inspection breaks this third-party site's cert chain, but the
        # private staging APIs need that same VPN to be reachable at all.
        # Only fake test data crosses this call, so skip verification here
        # unconditionally rather than forcing the whole run to disable it.
        verify=False,
    )
    if resp.status_code >= 400:
        sys.exit(f"4devs identity generation failed with {resp.status_code}: {resp.text}")
    try:
        person = json.loads(resp.text)[0]
    except (ValueError, IndexError, KeyError) as e:
        sys.exit(f"4devs returned an unparseable response ({e}): {resp.text[:400]}")

    identity = {
        "name": person["nome"],
        "document": re.sub(r"\D", "", person["cpf"]),
        "rg": re.sub(r"\D", "", person["rg"]),
        "mother_name": person["mae"],
        "gender": GENDER_CODE.get(person["sexo"], "M"),
        "birthdate": datetime.strptime(person["data_nasc"], "%d/%m/%Y").strftime(  # noqa: DTZ007
            "%Y-%m-%d"
        ),
        "mobile": re.sub(r"\D", "", person["celular"]),
        "address": {
            "zipcode": person["cep"],
            "street_name": person["endereco"],
            "building_number": str(person["numero"]),
            "neighborhood": person["bairro"],
            "city": person["cidade"],
            "state": person["estado"],
        },
    }
    print(f"  borrower: {identity['name']}  document: {identity['document']}")
    return identity


def generate_fake_bank_account() -> dict[str, str]:
    """Fetch a fresh, valid-format Banco do Brasil account from 4devs.com.br.

    Unlike the person generator, this tool replies with an HTML fragment,
    not JSON, so the fields are pulled out by id with a regex.
    """
    banner("06", "generate bank account (4devs, Banco do Brasil)")
    resp = SESSION.post(
        FOUR_DEVS_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.4devs.com.br",
            "Referer": "https://www.4devs.com.br/gerador_conta_bancaria",
            "X-Requested-With": "XMLHttpRequest",
        },
        data={"acao": "gerar_conta_bancaria", "estado": "", "banco": FOUR_DEVS_BANK_OPTION},
        timeout=30,
        verify=False,
    )
    if resp.status_code >= 400:
        sys.exit(f"4devs bank account generation failed with {resp.status_code}: {resp.text}")

    def extract(field_id: str) -> str:
        m = re.search(rf'id="{field_id}"[^>]*>([^<]+)<', resp.text)
        if not m:
            sys.exit(f"4devs bank account response missing '{field_id}': {resp.text[:400]}")
        return m.group(1).strip()

    account, _, account_digit = extract("conta_corrente").partition("-")
    bank_account = {
        "bank_code": BANCO_DO_BRASIL_CODE,
        "bank_name": BANCO_DO_BRASIL_NAME,
        "agency": extract("agencia"),
        "account": account,
        "account_digit": account_digit,
        "account_type": "checking",
    }
    print(f"  bank account: agency {bank_account['agency']}  account {account}-{account_digit}")
    return bank_account


def create_loan(base_url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    banner("01", "create loan (partner)")
    resp = SESSION.post(
        f"{base_url}/v1/loans", headers=partner_headers(api_key), json=payload, timeout=30
    )
    show(resp)
    raise_for(resp, "create loan")
    return resp.json()


def update_loan(base_url: str, api_key: str, loan_uid: str, payload: dict[str, Any]) -> None:
    banner("02", "update loan (partner)")
    resp = SESSION.patch(
        f"{base_url}/v1/loans/{loan_uid}",
        headers=partner_headers(api_key),
        json=payload,
        timeout=30,
    )
    show(resp)
    raise_for(resp, "update loan")


def request_credit_analysis(base_url: str, api_key: str, loan_uid: str) -> None:
    banner("03", "request credit analysis")
    resp = SESSION.put(
        f"{base_url}/v1/loans/{loan_uid}/credit-analysis",
        headers=partner_headers(api_key),
        json={},
        timeout=30,
    )
    show(resp)
    raise_for(resp, "request credit analysis")


def accept_offer(base_url: str, api_key: str, loan_uid: str, offer_uuid: str) -> None:
    banner("05", "accept offer")
    resp = SESSION.put(
        f"{base_url}/v1/loans/{loan_uid}/offers",
        headers=partner_headers(api_key),
        json={"uuid": offer_uuid},
        timeout=30,
    )
    show(resp)
    raise_for(resp, "accept offer")


def add_bank_account(base_url: str, api_key: str, loan_uid: str, bank_account: dict[str, str]) -> None:
    banner("07", "add bank account")
    resp = SESSION.post(
        f"{base_url}/v1/loans/{loan_uid}/bank-accounts",
        headers=partner_headers(api_key),
        json=bank_account,
        timeout=30,
    )
    show(resp)
    raise_for(resp, "add bank account")


def upload_document(
    base_url: str, api_key: str, loan_uid: str, document_type: str, b64: str, mime: str = "image/jpeg"
) -> None:
    banner("08", f"upload {document_type}")
    resp = SESSION.post(
        f"{base_url}/v1/loans/{loan_uid}/attachments",
        headers=partner_headers(api_key),
        json={
            "document_type": document_type,
            "mime_type": mime,
            "file_name": document_type,
            "data": b64,
        },
        timeout=30,
    )
    show(resp)
    raise_for(resp, f"upload {document_type}")


def accept_agreements(base_url: str, api_key: str, loan_uid: str) -> None:
    banner("09", "accept agreements")
    resp = SESSION.put(
        f"{base_url}/v1/loans/{loan_uid}/agreements",
        headers=partner_headers(api_key),
        json={
            "ip_address": "127.0.0.1",
            "accepted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        timeout=30,
    )
    show(resp)
    raise_for(resp, "accept agreements")


def submit_application(base_url: str, api_key: str, loan_uid: str) -> None:
    banner("10", "submit application")
    resp = SESSION.put(
        f"{base_url}/v1/loans/{loan_uid}/application",
        headers=partner_headers(api_key),
        timeout=30,
    )
    show(resp)
    raise_for(resp, "submit application")


def fraud_analysis_callback(private_url: str, api_key: str, loan_uid: str) -> None:
    banner("11", "fraud analysis callback (private)")
    deadline = time.monotonic() + int(cfg("POLL_TIMEOUT"))
    interval = int(cfg("POLL_INTERVAL"))
    while True:
        resp = SESSION.post(
            f"{private_url}/v1/loans/fraud-analysis/callback",
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            json={"loan_id": loan_uid, "action": "approve", "approved_by": "e2e_loan_flow"},
            timeout=30,
        )
        show(resp)
        if resp.status_code < 400:
            return
        if resp.status_code == 400 and "waiting_fraud_analysis" in resp.text:
            if time.monotonic() >= deadline:
                sys.exit(f"timed out waiting for waiting_approval; last body: {resp.text}")
            print(f"  loan still in waiting_fraud_analysis; retrying in {interval}s")
            time.sleep(interval)
            continue
        raise_for(resp, "fraud analysis callback")


def disbursal_release(private_url: str, api_key: str, loan_internal_id: int) -> None:
    banner("13", "disbursal release (private)")
    resp = SESSION.post(
        f"{private_url}/v1/loans/{loan_internal_id}/disbursal-release",
        headers=private_headers(api_key),
        timeout=30,
    )
    show(resp)
    raise_for(resp, "disbursal release")


POLL_REQUEST_TIMEOUT = 10  # seconds per GET /loans/{uid} during poll_until


def retrieve_loan(base_url: str, api_key: str, loan_uid: str) -> dict[str, Any]:
    resp = SESSION.get(
        f"{base_url}/v1/loans/{loan_uid}?offers=all&include_redirect=True",
        headers=partner_headers(api_key),
        timeout=POLL_REQUEST_TIMEOUT,
    )
    raise_for(resp, "retrieve loan")
    body = resp.json()
    return body.get("data", body) if isinstance(body, dict) else body


TERMINAL_FAILURE_STATES = {"denied", "cancelled", "expired"}


def poll_until(
    base_url: str,
    api_key: str,
    loan_uid: str,
    target_state: str,
    interval: int,
    timeout: int,
) -> dict[str, Any]:
    banner("POLL", f"waiting for current_state == {target_state}")
    deadline = time.monotonic() + timeout
    last_state: str | None = None
    while time.monotonic() < deadline:
        loan = retrieve_loan(base_url, api_key, loan_uid)
        print(loan)
        state = loan.get("current_state") or loan.get("status") or loan.get("state")
        if state != last_state:
            print(f"  state: {state}")
            last_state = state
        if state == target_state:
            return loan
        if state in TERMINAL_FAILURE_STATES and state != target_state:
            sys.exit(
                f"loan reached terminal failure state '{state}' while waiting for {target_state}"
            )
        time.sleep(interval)
    sys.exit(f"timed out waiting for {target_state}; last state was {last_state}")


def main() -> None:
    base_url = cfg("BASE_URL").rstrip("/")
    private_url = cfg("PRIVATE_BASE_URL").rstrip("/")
    api_key = cfg("PARTNER_API_KEY")
    interval = int(cfg("POLL_INTERVAL"))
    timeout = int(cfg("POLL_TIMEOUT"))
    credit_timeout = int(cfg("CREDIT_ANALYSIS_TIMEOUT"))
    income = float(cfg("BORROWER_INCOME"))

    selfie = os.environ.get("SELFIE_B64") or PLACEHOLDER_JPEG_B64
    document_front = os.environ.get("DOCUMENT_FRONT_B64") or PLACEHOLDER_JPEG_B64
    life_proof = os.environ.get("LIFE_PROOF_B64") or PLACEHOLDER_JPEG_B64

    print(f"public  : {base_url}")
    print(f"private : {private_url}")

    borrower = generate_fake_borrower()
    borrower_name = os.environ.get("BORROWER_NAME") or borrower["name"]
    borrower_email = os.environ.get("BORROWER_EMAIL") or (
        f"itest+{random.randint(1000, 99999)}@noverde.tests.io"
    )

    requested_amount = float(os.environ.get("REQUESTED_AMOUNT", "500.00"))
    requested_period = int(os.environ.get("REQUESTED_PERIOD", "8"))
    request_installment = float(
        os.environ.get("REQUEST_INSTALLMENT", round(requested_amount / requested_period, 2))
    )

    loan_payload = {
        "document": borrower["document"],
        "name": borrower_name,
        "birthdate": os.environ.get("BORROWER_BIRTHDATE") or borrower["birthdate"],
        "email": borrower_email,
        "mobile_number": os.environ.get("BORROWER_MOBILE") or borrower["mobile"],
        "income": income,
        "employment_status": os.environ.get("BORROWER_EMPLOYMENT", "employee"),
        "requested_amount": requested_amount,
        "requested_period": requested_period,
        "requested_payday": int(os.environ.get("REQUESTED_PAYDAY", "5")),
        "request_installment": request_installment,
        "reason": os.environ.get("LOAN_REASON", "travel"),
        "address": {
            "zipcode": os.environ.get("ADDRESS_ZIPCODE") or "01010-000",
            "street_name": os.environ.get("ADDRESS_STREET") or borrower["address"]["street_name"],
            "building_number": os.environ.get("ADDRESS_NUMBER") or borrower["address"]["building_number"],
            "neighborhood": os.environ.get("ADDRESS_NEIGHBORHOOD") or borrower["address"]["neighborhood"],
            "city": os.environ.get("ADDRESS_CITY") or borrower["address"]["city"],
            "state": os.environ.get("ADDRESS_STATE") or borrower["address"]["state"],
        },
        "fingerprint": {
            "device_info": "Mozilla/5.0 (X11; Linux x86_64) e2e_loan_flow",
        },
    }
    loan = create_loan(base_url, api_key, loan_payload)
    loan_uid = loan.get("uid") or loan.get("loan_id") or loan.get("id")
    if not loan_uid:
        sys.exit(f"create loan response missing uid: {json.dumps(loan)[:400]}")
    print(f"loan_uid = {loan_uid}")

    update_payload = {
        "marital_status": os.environ.get("BORROWER_MARITAL_STATUS", "single"),
        "document_infos": {
            "document_number": borrower["rg"],
            "issuer": "SSP",
            "issuer_state": loan_payload["address"]["state"],
            "issue_date": "2010-01-01",
            "document_kind": "rg",
        },
        "gender": borrower["gender"],
        "mother_name": borrower["mother_name"],
    }
    update_loan(base_url, api_key, loan_uid, update_payload)

    request_credit_analysis(base_url, api_key, loan_uid)
    loan = poll_until(base_url, api_key, loan_uid, "proposal", interval, credit_timeout)

    offer_uuid = ""
    offers = loan.get("offers") or []
    if offers:
        first = offers[0]
        offer_uuid = first.get("uuid") or first.get("id") or ""
    if not offer_uuid:
        sys.exit(f"no offer uuid found on loan: {json.dumps(loan)[:400]}")

    accept_offer(base_url, api_key, loan_uid, offer_uuid)
    bank_account = generate_fake_bank_account()
    add_bank_account(base_url, api_key, loan_uid, bank_account)
    upload_document(base_url, api_key, loan_uid, "selfie", selfie)
    upload_document(base_url, api_key, loan_uid, "document_front", document_front)
    upload_document(base_url, api_key, loan_uid, "life_proof", life_proof, mime="image/png")
    accept_agreements(base_url, api_key, loan_uid)
    submit_application(base_url, api_key, loan_uid)

    fraud_analysis_callback(private_url, api_key, loan_uid)
    loan = poll_until(base_url, api_key, loan_uid, "waiting_lending", interval, timeout)

    # Disbursal now runs automatically on the backend; just wait for it.
    loan = poll_until(base_url, api_key, loan_uid, "lent", interval, timeout)

    banner("DONE", f"loan {loan_uid} reached LENT")
    print(json.dumps(loan, indent=2)[:1500])


if __name__ == "__main__":
    main()
