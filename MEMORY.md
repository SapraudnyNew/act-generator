# MEMORY.md — Agent Index

## Identity
Agent (Claude Sonnet). Owner: Алексей Марушевский (@AlexMarksman). Workspace: ~/act-generator.

## Active Projects
act-generator — генерация актов сдачи-приёмки из PDF счёт-договоров. Протестировано на счетах 1128–1131. Шаблон и правила стабильны.

## Key Rules
- Дата акта = дата окончания услуг из счёта (не дата договора)
- `payment_link` — запрашивать для каждого счёта отдельно
- `signatory` — родительный падеж (шапка), `signatory_short` — именительный Фамилия И.О. (подпись)
- `authority` — «Устава» по умолчанию, иначе «Доверенности № X от ДД.ММ.ГГГГ г.»
- Если банковских реквизитов нет в счёте — запросить карточку предприятия
- Имя файла: `Акт к Счет-договору № {N} от {date}г.docx`

## Details
Полная документация, JSON-схема, правила: https://github.com/SapraudnyNew/act-generator/blob/main/README.md
