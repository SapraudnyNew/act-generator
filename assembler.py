"""
assembler.py

Сборка итогового docx-акта из шаблона.
QR-код не используется — ссылка передаётся текстом в пункте 3.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Разворачивает вложенный dict в плоский: {"contractor.name": "..."}."""
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


def _short_name(full_name: str) -> str:
    """
    Преобразует полное ФИО в формат «Фамилия И.О.»
    Например: «Малышев Максим Вадимович» → «Малышев М.В.»
    Работает для 2 и 3 слов.
    """
    parts = full_name.strip().split()
    if len(parts) == 1:
        return full_name
    initials = "".join(p[0].upper() + "." for p in parts[1:])
    return f"{parts[0]} {initials}"


def _replace_in_paragraph(paragraph, replacements: dict[str, str]) -> None:
    """Заменяет {{KEY}} в параграфе, сохраняя форматирование первого рана."""
    full_text = "".join(run.text for run in paragraph.runs)
    new_text = full_text
    for key, value in replacements.items():
        new_text = new_text.replace(f"{{{{{key}}}}}", value)
    if new_text != full_text:
        for i, run in enumerate(paragraph.runs):
            run.text = new_text if i == 0 else ""


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------

def assemble(
    data: dict[str, Any],
    template_path: str | Path = "template.docx",
    output_path: str | Path | None = None,
) -> Path:
    """
    Собирает документ акта из шаблона и данных.

    Args:
        data:          Валидированный JSON-словарь из validator.
        template_path: Путь к шаблону .docx.
        output_path:   Куда сохранить результат. Если None — генерируется автоматически.

    Returns:
        Path к готовому файлу.
    """
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")

    if output_path is None:
        inv = data.get("invoice_number", "act").replace("/", "-").replace(" ", "_")
        output_path = Path(f"act_{inv}.docx")
    output_path = Path(output_path)

    # Добавляем короткие имена подписантов
    import copy
    data = copy.deepcopy(data)
    for party in ("contractor", "client"):
        p = data.get(party, {})
        if p.get("signatory"):
            p["signatory_short"] = _short_name(p["signatory"])

    flat = _flatten(data)

    doc = Document(str(template_path))

    # Обход всех параграфов (включая ячейки таблиц)
    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    for para in all_paragraphs:
        _replace_in_paragraph(para, flat)

    doc.save(str(output_path))
    return output_path
