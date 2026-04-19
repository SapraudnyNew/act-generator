"""
main.py — точка входа

Использование:
    python main.py --invoice invoice.pdf
    python main.py --invoice invoice.pdf --folder-id 1BxiMVs0XRA...
    python main.py --invoice invoice.pdf --no-upload  # только собрать документ
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from extractor import extract_from_file
from validator import validate
from assembler import assemble
from drive_uploader import upload_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Генерация акта выполненных работ на основе счёта"
    )
    parser.add_argument("--invoice",   required=True,  help="Путь к файлу счёта (pdf/docx/txt)")
    parser.add_argument("--template",  default="template.docx", help="Путь к шаблону акта")
    parser.add_argument("--output",    default=None,   help="Имя выходного файла")
    parser.add_argument("--folder-id", default=os.getenv("DRIVE_FOLDER_ID"),
                        help="ID папки Google Drive")
    parser.add_argument("--no-upload", action="store_true",
                        help="Не загружать на Google Drive")
    parser.add_argument("--no-public", action="store_true",
                        help="Не открывать публичный доступ")
    args = parser.parse_args()

    # --- Шаг 1: экстракция ---
    print(f"🔍  Анализирую {args.invoice} ...")
    data = extract_from_file(args.invoice)
    print("✅ Данные извлечены:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # --- Шаг 2: валидация ---
    print("\n📝  Валидация данных ...")
    try:
        data = validate(data)
    except ValueError as exc:
        print(f"\n❌  {exc}")
        sys.exit(1)
    print("✅ Валидация пройдена")

    # --- Шаг 3: сборка документа ---
    print("\n📎  Собираю документ ...")
    output_file = assemble(
        data,
        template_path=args.template,
        output_path=args.output,
    )
    print(f"✅ Готово: {output_file}")

    # --- Шаг 4: загрузка на Google Drive ---
    if not args.no_upload:
        if not args.folder_id:
            print("\n⚠️  DRIVE_FOLDER_ID не задан. Добавь в .env или используй --folder-id.")
            sys.exit(1)
        print("\n☁️  Загружаю на Google Drive ...")
        link = upload_file(
            file_path=output_file,
            folder_id=args.folder_id,
            make_public=not args.no_public,
        )
        print(f"✅ Готово! Ссылка: {link}")
    else:
        print(f"\n💾  Файл сохранён локально: {output_file}")


if __name__ == "__main__":
    main()
