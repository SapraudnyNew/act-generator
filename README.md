# Act Generator

Система генерации актов выполненных работ на основе входящих счетов.

## Архитектура

```
invoice (pdf/doc/txt)
       │
       ▼
┌─────────────┐
│  extractor  │  Claude Sonnet 4.6 via OpenRouter
│             │  → строгий JSON с реквизитами
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  validator  │  часы × ставка, обязательные поля
│             │  интерактивный запрос недостающего
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  assembler  │  вставка переменных в docx-шаблон
│             │  генерация QR-кода
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   drive     │  загрузка на Google Drive (ADC/gcloud)
│  uploader   │  → прямая ссылка
└─────────────┘
```

## Структура проекта

```
act-generator/
├── extractor.py       # LLM-экстрактор данных из счёта
├── validator.py       # Валидация логики и реквизитов
├── assembler.py       # Сборка итогового docx
├── drive_uploader.py  # Загрузка на Google Drive
├── main.py            # Точка входа
├── template.docx      # Шаблон акта (добавить вручную)
├── requirements.txt
└── .env.example
```

## Установка

```bash
pip install -r requirements.txt
```

## Аутентификация Google Drive

Используется Application Default Credentials через gcloud CLI:

```bash
gcloud auth application-default login
```

Либо через переменную окружения:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## Использование

```bash
python main.py --invoice invoice.pdf --folder-id YOUR_DRIVE_FOLDER_ID
```

## Переменные окружения

Скопируй `.env.example` в `.env` и заполни:

```
OPENROUTER_API_KEY=your_key_here
DRIVE_FOLDER_ID=your_google_drive_folder_id
```
