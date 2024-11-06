import pandas as pd
from datetime import datetime
import logging
import csv
import helper
import clicksign_api
import settings

def read_file(path):
  result = []

  df = pd.read_csv(path, na_filter=False)

  df["lent_at"] = pd.to_datetime(df["lent_at"])
  df["due_date"] = pd.to_datetime(df["due_date"])
  df["entry_due_date"] = pd.to_datetime(df["entry_due_date"])
  df["first_original_due_date"] = pd.to_datetime(df["first_original_due_date"])
  df["last_original_due_date"] = pd.to_datetime(df["last_original_due_date"])
  df["value"] = df["value"].round(decimals = 2)

  grouped = df.groupby('loan_id')

  for loan_id, group in grouped:
    item = {}

    if set(group['type'].unique()) != set(['original', 'current']):
      raise ValueError(f"Invalid type for loan_id {loan_id}")

    original_installments = group.loc[group['type'] == "original"]
    current_installments = group.loc[group['type'] == "current"]

    first = group.head(1).to_dict('records')[0]

    item["loan_id"] = first.get("loan_id", "")
    item["lecca_id"] = first.get("lecca_id", "")
    item["borrower_name"] = first.get("borrower_name", "")
    item["borrower_document"] = first.get("borrower_document", "")
    item["borrower_address"] = first.get("borrower_address", "")
    item["lent_at"] = helper.format_date(first.get("lent_at", ""))
    item["contract_value"] = helper.format_currency(first.get("contract_value", ""))
    item["iof_fee"] = helper.format_currency(first.get("iof_fee", ""))
    item["annual_interest_rate"] = helper.format_number(first.get("annual_interest_rate", ""), 4)
    item["monthly_percentage_rate"] = helper.format_number(first.get("monthly_percentage_rate", ""), 4)
    item["annual_percentage_rate"] = helper.format_number(first.get("annual_percentage_rate", ""), 4)
    item["net_value"] = helper.format_currency(first.get("net_value", ""))
    item["partner_fee"] = helper.format_currency(first.get("partner_fee", ""))
    item["installment_value"] = helper.format_currency(first.get("installment_value", ""))
    item["period"] = first.get("period", "")
    item["interest_rate"] = first.get("interest_rate", "")
    item["first_original_due_date"] = helper.format_date(first.get("first_original_due_date", ""))
    item["last_original_due_date"] = helper.format_date(first.get("last_original_due_date", ""))
    item["date_signature"] = helper.format_extensive_date(datetime.now())
    
    item["installments_table"] = {
        "original": {
            "installments": original_installments[["number", "due_date", "value", "entry_amount", "entry_due_date"]].to_dict(orient='records'),
            "total_value": original_installments["value"].sum()
        },
        "current": {
            "installments": current_installments[["number", "due_date", "value", "entry_amount", "entry_due_date"]].to_dict(orient='records'),
            "total_value": current_installments["value"].sum()
        }
    }

    result.append(item)

  logging.info(f"Total Contracts {len(result)}")
  return result

def create_table(table: dict) -> str:
    data_original = table["original"]
    data_current = table["current"]

    entry_amount = data_current["installments"][0]["entry_amount"]
    entry_due_date = data_current["installments"][0]["entry_due_date"]

    installments_original_table = ""
    for installment in data_original["installments"]:
        installments_original_table += ("         {}                         {}                 R$ {}\n".format(installment["number"], installment["due_date"].strftime('%d/%m/%Y'), helper.format_currency(installment["value"])))

    installments_current_table = ""
    for installment in data_current["installments"]:
        installments_current_table += ("          {}                          {}                 R$ {}\n".format(installment["number"], installment["due_date"].strftime('%d/%m/%Y'), helper.format_currency(installment["value"])))

    installments_table = f"""
    FLUXO DE PAGAMENTO ORIGINAL - PARCELAS RESTANTES

Número de Parcelas   |   Data de Vencimento   |   Valor da Parcela
{installments_original_table}

    Total                                  R$ {helper.format_currency(data_original["total_value"])}

-----------------------------------------------------------

    FLUXO DE PAGAMENTO ATUAL - ADITAMENTO CONTRATUAL

Entrada no valor de R$ {helper.format_currency(entry_amount)} com vencimento {entry_due_date.strftime('%d/%m/%Y')}
e demais parcelas de acordo com o novo fluxo de pagamento:

Número de Parcelas | Data de Vencimento | Valor da Parcela
{installments_current_table}

    Total                                  R$ {helper.format_currency(data_current["total_value"])}

"""

    return installments_table

def create(data: list):
    df_database = pd.read_csv("./documents_database.csv", quoting=csv.QUOTE_ALL, na_filter=False)

    created, existing, error = 0, 0, 0

    for document in data:
        loan_id = document["loan_id"]
        existing_loans = df_database[df_database['loan_id'] == loan_id].index

        if len(existing_loans) > 1:
            logging.error(f"Duplicated loan_id {loan_id}")
            error += 1
            continue

        if len(existing_loans) == 1:
            existing += 1
            continue

        table_data = document["installments_table"]

        if isinstance(table_data, dict):
            table = create_table(table_data)
            document["installments_table"] = table

        document_key = clicksign_api.create_document(document)
        logging.info(f"Create Sucess Document ClickSign loan_id {loan_id}")

        if not document_key:
            error += 1
            continue
        
        row = {
          "loan_id": loan_id,
          "document_key": document_key,
          "signer_key": "",
          "request_signature_key": "",
          "creted_at": datetime.now()
        }

        # new_row_df = pd.DataFrame([row])
        df_database = pd.concat([df_database, pd.DataFrame([row])], ignore_index=True)
        logging.info(f"Concact Document Sucess loan_id {loan_id}")

        # df_database = df_database.append(row, ignore_index = True)

        created += 1

    df_database.to_csv("./documents_database.csv", index = False, quoting=csv.QUOTE_ALL)

    return created, existing, error

def add_signatary():
    df_database = pd.read_csv("./documents_database.csv", quoting=csv.QUOTE_ALL, na_filter=False)

    created, existing, error = 0, 0, 0

    for i, row in df_database.iterrows():
        existing_signer_key = df_database.at[i, "signer_key"]
        if len(existing_signer_key) > 0:
            existing += 1
            continue

        document_key = df_database.at[i, "document_key"]
        added = clicksign_api.add_signatary(settings.signer_key, document_key)

        if not added:
            error += 1
            continue

        df_database.at[i, "signer_key"] = settings.signer_key

        created += 1

    df_database.to_csv("./documents_database.csv", index = False, quoting=csv.QUOTE_ALL)

    return created, existing, error

def create_batch_and_notification() -> None:
    df_database = pd.read_csv("./documents_database.csv", quoting=csv.QUOTE_ALL, na_filter=False)

    grouped = df_database.groupby('signer_key')
    for signer_key, group in grouped:
        documents_keys = group["document_key"].tolist()

        while len(documents_keys) > 0:
            batch = documents_keys[:500]
            del documents_keys[:500]

            request_signature_key = clicksign_api.create_batch(signer_key, batch)

            if request_signature_key:
                group["request_signature_key"] = request_signature_key
                clicksign_api.notification(request_signature_key, settings.notification_message)

    df_database.to_csv("./documents_database.csv", index = False, quoting=csv.QUOTE_ALL)
