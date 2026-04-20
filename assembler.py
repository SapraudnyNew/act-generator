"""
assembler.py

Сборка итогового docx-акта из шаблона.

Правила полей подписанта:
  signatory        — родительный падеж, полное ФИО (вводный абзац)
  signatory_short  — именительный, Фамилия И.О. (строка подписи)
  authority        — «Устава» / «Доверенности № X от...» / пустая строка для ИП
                     Если пусто — фраза «действующего на основании ...» убирается целиком

Правило имени файла:
  «Акт к Счет-договору № {invoice_number} от {invoice_date}г.docx»
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from docx import Document


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    result: dict[str, str] = {}
    for k, v in data.items():
        full_key = f"{prefix}{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten(v, prefix=full_key + "."))
        elif v is None:
            result[full_key] = ""
        else:
            result[full_key] = str(v)
    return result


def _apply_replacements(text: str, replacements: dict[str, str]) -> str:
    """Заменяет {{KEY}} → value. Если authority пусто — убирает фразу целиком."""
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)

    # Убираем «, действующего на основании ,» и похожие артефакты когда authority пусто
    text = re.sub(r",?\s*действующ\w+ на основании\s*,", ",", text)
    text = re.sub(r",?\s*действующ\w+ на основании\s*\.?$", "", text)
    # Убираем двойные запятые и пробелы
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text


def _replace_in_paragraph(paragraph, replacements: dict[str, str]) -> None:
    full_text = "".join(run.text for run in paragraph.runs)
    new_text = _apply_replacements(full_text, replacements)
    if new_text != full_text:
        for i, run in enumerate(paragraph.runs):
            run.text = new_text if i == 0 else ""


def _make_filename(data: dict[str, Any]) -> str:
    num = data.get("invoice_number", "")
    date = data.get("invoice_date", "")
    return f"Акт к Счет-договору № {num} от {date}г.docx"


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------

def assemble(
    data: dict[str, Any],
    template_path: str | Path = "template.docx",
    output_path: str | Path | None = None,
) -> Path:
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")

    if output_path is None:
        output_path = Path(_make_filename(data))
    output_path = Path(output_path)

    data = copy.deepcopy(data)
    flat = _flatten(data)

    doc = Document(str(template_path))

    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    for para in all_paragraphs:
        _replace_in_paragraph(para, flat)

    doc.save(str(output_path))
    return output_path
