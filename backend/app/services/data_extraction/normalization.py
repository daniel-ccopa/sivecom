import re
import unicodedata
from decimal import Decimal, InvalidOperation


MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_text(value: str) -> str:
    lowered = value.lower()
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", lowered)
        if not unicodedata.combining(char)
    )
    return normalize_spaces(without_accents)


def normalize_ruc(value: str) -> str:
    return re.sub(r"\D", "", value)


def normalize_amount(value: str) -> str:
    clean = normalize_spaces(value).replace("S/.", "").replace("S/", "")
    clean = clean.replace(" ", "")
    if "," in clean and "." in clean:
        decimal_separator = "," if clean.rfind(",") > clean.rfind(".") else "."
        thousands_separator = "." if decimal_separator == "," else ","
        clean = clean.replace(thousands_separator, "")
        clean = clean.replace(decimal_separator, ".")
    elif "," in clean:
        before, after = clean.rsplit(",", 1)
        clean = before.replace(",", "") + "." + after if len(after) == 2 else clean.replace(",", "")
    elif "." in clean:
        before, after = clean.rsplit(".", 1)
        clean = before.replace(".", "") + "." + after if len(after) == 2 else clean.replace(".", "")

    try:
        return f"{Decimal(clean):.2f}"
    except InvalidOperation:
        return value


def normalize_numeric_date(day: str, month: str, year: str) -> str:
    normalized_year = int(year)
    if normalized_year < 100:
        normalized_year += 2000
    return f"{normalized_year:04d}-{int(month):02d}-{int(day):02d}"


def normalize_textual_date(day: str, month_name: str, year: str) -> str:
    month = MONTHS.get(normalize_text(month_name))
    if month is None:
        return normalize_spaces(f"{day} de {month_name} de {year}")
    return f"{int(year):04d}-{month:02d}-{int(day):02d}"


def clean_line_value(value: str) -> str:
    cleaned = normalize_spaces(value)
    return cleaned.strip(" :-|")
