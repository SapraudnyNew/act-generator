"""
drive_uploader.py

Загружает файл на Google Drive и возвращает прямую ссылку.
Аутентификация: Application Default Credentials (gcloud CLI / GWS).

Использование:
    from drive_uploader import upload_file

    link = upload_file(
        file_path="act_2024_001.docx",
        folder_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs",  # опционально
        make_public=True,
    )
    print(link)  # https://drive.google.com/file/d/.../view
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from google.auth import default as google_auth_default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# MIME-типы для основных форматов
_MIME_MAP: dict[str, str] = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_service():
    """Создаёт авторизованный клиент Drive API v3 через ADC."""
    credentials, _ = google_auth_default(scopes=_SCOPES)
    if hasattr(credentials, "expired") and credentials.expired:
        credentials.refresh(Request())
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def upload_file(
    file_path: str | Path,
    folder_id: Optional[str] = None,
    make_public: bool = True,
    file_name: Optional[str] = None,
) -> str:
    """
    Загружает файл на Google Drive.

    Args:
        file_path:    Путь к локальному файлу.
        folder_id:    ID папки на Drive. Если None — загружает в корень.
        make_public:  Если True — открывает доступ по ссылке (anyoneWithLink reader).
        file_name:    Имя файла на Drive. По умолчанию — оригинальное имя.

    Returns:
        Прямая ссылка на файл: https://drive.google.com/file/d/{id}/view

    Raises:
        FileNotFoundError: Если локальный файл не найден.
        HttpError:         При ошибке Drive API.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    suffix = file_path.suffix.lower()
    mime_type = _MIME_MAP.get(suffix, "application/octet-stream")
    name_on_drive = file_name or file_path.name

    service = _get_service()

    # Метаданные файла
    file_metadata: dict = {"name": name_on_drive}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

    try:
        uploaded = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, name, webViewLink",
            )
            .execute()
        )
    except HttpError as exc:
        raise HttpError(exc.resp, exc.content, uri=exc.uri) from exc

    file_id: str = uploaded["id"]

    if make_public:
        _set_public_reader(service, file_id)

    link = uploaded.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
    return link


def _set_public_reader(service, file_id: str) -> None:
    """Открывает доступ к файлу по ссылке (читатель, без логина)."""
    permission = {
        "type": "anyone",
        "role": "reader",
    }
    service.permissions().create(
        fileId=file_id,
        body=permission,
        fields="id",
    ).execute()


# ---------------------------------------------------------------------------
# Быстрый тест из командной строки
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Загрузить файл на Google Drive")
    parser.add_argument("file", help="Путь к файлу")
    parser.add_argument("--folder-id", default=None, help="ID папки на Drive")
    parser.add_argument("--no-public", action="store_true", help="Не открывать публичный доступ")
    args = parser.parse_args()

    url = upload_file(
        file_path=args.file,
        folder_id=args.folder_id,
        make_public=not args.no_public,
    )
    print(f"✅ Загружено: {url}")
