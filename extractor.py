"""
extractor.py

Экстрактор данных из счёта.

MODEL работает только как экстрактор: получает текст счёта, возвращает строгий JSON.
Текст акта модель НЕ генерирует.

Вход файла:
    Текст счёта (pdf/doc/txt конвертируется локально до отправки)

Схема выходного JSON:
    {
        "invoice_number":   "№ счёта",
        "invoice_date":     "дата счёта (DD.MM.YYYY)",
        "act_date":         "дата акта (DD.MM.YYYY) — обычно = дата счёта",
        "service_name":     "название услуги",
        "hours":            часы (число),
        "rate":             ставка за час (число),
        "total_amount":     итоговая сумма (число),
        "currency":         "валюта (RUB / USD / EUR …)",
        "contractor": {
            "name":         "название организации или ФИО ИП",
            "inn":          "ИНН",
            "kpp":          "КПП или null",
            "address":      "юрадрес",
            "signatory":    "ФИО подписанта или null",
            "position":     "должность подписанта или null"
        },
        "client": {
            "name":         "название организации",
            "inn":          "ИНН",
            "kpp":          "КПП или null",
            "address":      "юрадрес",
            "signatory":    "ФИО подписанта или null",
            "position":     "должность подписанта или null"
        },
        "payment_link":     "ссылка для QR-кода или null"
    }
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

# ---------------------------------------------------------------------------
# Конфиг
# ---------------------------------------------------------------------------

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "anthropic/claude-sonnet-4-6"  # через OpenRouter

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# ---------------------------------------------------------------------------
# Системный промпт (кэшируется на стороне OpenRouter)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a strict data extractor. Your only task is to parse the invoice text 
and return a single JSON object — no markdown, no explanation, no extra text.

Required JSON schema:
{
  "invoice_number":  string,
  "invoice_date":    string (DD.MM.YYYY),
  "act_date":        string (DD.MM.YYYY),
  "service_name":    string,
  "hours":           number | null,
  "rate":            number | null,
  "total_amount":    number,
  "currency":        string,
  "contractor": {
    "name":       string,
    "inn":        string,
    "kpp":        string | null,
    "address":    string,
    "signatory":  string | null,
    "position":   string | null
  },
  "client": {
    "name":       string,
    "inn":        string,
    "kpp":        string | null,
    "address":    string,
    "signatory":  string | null,
    "position":   string | null
  },
  "payment_link": string | null
}

Rules:
- Return ONLY valid JSON. No markdown fences, no commentary.
- If a field is not found in the document, set it to null.
- Numbers must be numeric types, not strings.
- Dates must be in DD.MM.YYYY format.
- Do not invent data. Only extract what is present in the text.
"""

# ---------------------------------------------------------------------------
# Локальная предобработка: конвертация файла в текст
# ---------------------------------------------------------------------------

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
    """
    Конвертирует pdf / docx / doc / txt в плоский текст.
    Бинарные файлы хранятся локально — модели не получают бинарные данные.
    """
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
        # Попытка читать как текст
        return _read_txt(path)


# ---------------------------------------------------------------------------
# Основной экстрактор
# ---------------------------------------------------------------------------

def extract(invoice_text: str) -> dict[str, Any]:
    """
    Отправляет текст счёта в модель, возвращает парсенный JSON-объект.

    Args:
        invoice_text: Плоский текст счёта.

    Returns:
        dict со всеми извлечёнными полями.

    Raises:
        ValueError: Если модель вернула не валидный JSON.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": invoice_text},
        ],
        temperature=0,       # детерминированный режим
        max_tokens=1024,     # достаточно для JSON-ответа
    )

    raw = response.choices[0].message.content.strip()

    # Очищаем маркдаун на случай, если модель всё же добавила ``строки
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Модель вернула невалидный JSON:\n{raw}") from exc

    return data


def extract_from_file(file_path: str | Path) -> dict[str, Any]:
    """Удобный враппер: файл → текст → JSON."""
    text = load_invoice_text(file_path)
    return extract(text)


# ---------------------------------------------------------------------------
# CLI-тест
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="Экстракт данных из счёта")
    parser.add_argument("file", help="Путь к файлу счёта (pdf/docx/txt)")
    args = parser.parse_args()

    result = extract_from_file(args.file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
