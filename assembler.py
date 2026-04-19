"""
assembler.py

Сборка итогового docx-акта из шаблона.

Шаблон template.docx должен содержать теги в формате {{KEY}},
например: {{invoice_number}}, {{contractor.name}}, {{qr_image}}

{{qr_image}} — специальный тег: заменяется вставкой изображения QR-кода.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Cm


# ---------------------------------------------------------------------------
# QR-код
# ---------------------------------------------------------------------------

def _generate_qr(url: str, size_px: int = 300) -> Path:
    """Генерирует PNG с QR-кодом в временную директорию."""
    import qrcode  # type: ignore

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Замена тегов в документе
# ---------------------------------------------------------------------------

def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Разворачивает вложенный dict в плоский: {\"contractor.name\": \"...\"}."""
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


def _replace_in_paragraph(paragraph, replacements: dict[str, str]) -> None:
    """Заменяет {{KEY}} в параграфе, сохраняя форматирование первого рана."""
    full_text = "".join(run.text for run in paragraph.runs)
    new_text = full_text
    for key, value in replacements.items():
        new_text = new_text.replace(f"{{{{{key}}}}}", value)
    if new_text != full_text:
        # Сбрасываем всё в первый ран, остальные очищаем
        for i, run in enumerate(paragraph.runs):
            run.text = new_text if i == 0 else ""


def _insert_qr_image(paragraph, qr_path: Path, width_cm: float = 3.0) -> None:
    """Заменяет текст параграфа на изображение QR-кода."""
    for run in paragraph.runs:
        run.text = ""
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    run.add_picture(str(qr_path), width=Cm(width_cm))


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

    # Автоматическое имя выходного файла
    if output_path is None:
        inv = data.get("invoice_number", "act").replace("/", "-").replace(" ", "_")
        output_path = Path(f"act_{inv}.docx")
    output_path = Path(output_path)

    # QR-код
    qr_path: Path | None = None
    payment_link = data.get("payment_link")
    if payment_link:
        qr_path = _generate_qr(payment_link)

    # Разворачиваем вложенные поля
    flat = _flatten(data)

    doc = Document(str(template_path))

    QR_TAG = "{{qr_image}}"

    # Обход всех параграфов (включая ячейки таблиц)
    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    for para in all_paragraphs:
        full_text = "".join(r.text for r in para.runs)
        if QR_TAG in full_text and qr_path:
            _insert_qr_image(para, qr_path)
        else:
            _replace_in_paragraph(para, flat)

    doc.save(str(output_path))

    # Удаляем временный QR-файл
    if qr_path and qr_path.exists():
        qr_path.unlink()

    return output_path
