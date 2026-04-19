"""
extractor.py

Экстрактор данных из счёта.

MODEL работает только как экстрактор: получает текст счёта, возвращает строгий JSON.
Текст акта модель НЕ генерирует.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "anthropic/claude-sonnet-4-6"

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

SYSTEM_PROMPT = """\
You are a strict data extractor. Your only task is to parse the invoice text 
and return a single JSON object — no markdown, no explanation, no extra text.

Required JSON schema:
{
  "invoice_number":     string,
  "invoice_date":       string (DD.MM.YYYY),
  "act_date":           string (DD.MM.YYYY),
  "service_name":       string,
  "hours":              number | null,
  "hours_text":         string | null,
  "rate":               number | null,
  "total_amount":       number,
  "total_amount_text":  string,
  "currency":           string,
  "contractor": {
    "name":              string,
    "inn":               string,
    "kpp":               string | null,
    "address":           string,
    "signatory":         string | null,
    "position":          string | null,
    "bank_account":      string | null,
    "bank_name":         string | null,
    "bank_corr_account": string | null,
    "bank_bik":          string | null,
    "phone":             string | null
  },
  "client": {
    "name":              string,
    "inn":               string,
    "kpp":               string | null,
    "address":           string,
    "signatory":         string | null,
    "position":          string | null,
    "bank_account":      string | null,
    "bank_name":         string | null,
    "bank_corr_account": string | null,
    "bank_bik":          string | null,
    "phone":             string | null
  },
  "payment_link": string | null
}

Rules:
- Return ONLY valid JSON. No markdown fences, no commentary.
- If a field is not found in the document, set it to null.
- Numbers must be numeric types, not strings.
- Dates must be in DD.MM.YYYY format.
- hours_text: number of hours written out in words in Russian (e.g. "пятнадцать").
- total_amount_text: total sum written out in words in Russian (e.g. "Сто шестьдесят восемь тысяч триста").
- Do not invent data. Only extract what is present in the text.
"""


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    import pdfplumber
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


def _read_docx(path: Path) -> str:
    from docx import Document
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_invoice_text(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    elif suffix in (".docx", ".doc"):
        return _read_docx(path)
    elif suffix == ".txt":
        return _read_txt(path)
    else:
        return _read_txt(path)


def extract(invoice_text: str) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": invoice_text},
        ],
        temperature=0,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(line for line in lines if not line.strip().startswith("```"))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Модель вернула невалидный JSON:\n{raw}") from exc
    return data


def extract_from_file(file_path: str | Path) -> dict[str, Any]:
    text = load_invoice_text(file_path)
    return extract(text)


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="Экстракт данных из счёта")
    parser.add_argument("file", help="Путь к файлу счёта (pdf/docx/txt)")
    args = parser.parse_args()

    result = extract_from_file(args.file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
