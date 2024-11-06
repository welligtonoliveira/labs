from datetime import date, datetime

def format_currency(value) -> str:

    if (
        not isinstance(value, float)
        and not isinstance(value, int)
    ):
        return str(value)

    text = f"{float(value):_.2f}"
    text = text.replace(".", ",").replace("_", ".")

    return text

def format_number(value, digits) -> str:

    if (not isinstance(value, float)):
        return str(value)

    text = f"{float(value):.{digits}f}"
    text = text.replace(".", ",")

    return text

def format_date(value) -> str:

  if (
      not value
      or (not isinstance(value, datetime) and not isinstance(value, date))
  ):
      return str(value)

  return value.strftime('%d/%m/%Y')

def format_extensive_date(value):
  if (
      not value
      or (not isinstance(value, datetime) and not isinstance(value, date))
  ):
    return str(value)

  month_name = {
      '1': 'janeiro',
      '2': 'fevereiro',
      '3': 'março',
      '4': 'abril',
      '5': 'maio',
      '6': 'junho',
      '7': 'julho',
      '8': 'agosto',
      '9': 'setembro',
      '10': 'outubro',
      '11': 'novembro',
      '12': 'dezembro'        
  }

  written = f'{str(value.day)} de {month_name[str(value.month)]} de {str(value.year)}'

  return written
