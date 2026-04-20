"""
test_run_1131.py — Скайори, счёт-договор №1131
Файл: «Акт к Счет-договору № 1131 от 25.02.2026г.docx»
"""
from assembler import assemble

data = {
    "invoice_number":    "1131",
    "invoice_date":      "25.02.2026",
    "act_date":          "23.03.2026",
    "service_name":      "консультационные услуги по теме «Маркетинг ключевых клиентов»",
    "hours":             15,
    "hours_text":        "пятнадцать",
    "rate":              6600,
    "total_amount":      "99 000,00",
    "total_amount_text": "Девяносто девять тысяч",
    "currency":          "RUB",
    "payment_link":      "https://read.paperflite.com/collections/69a1394181372d5611f43ad8",
    "client": {
        "name":              "ООО «Скайори»",
        "inn":               "5905061802",
        "kpp":               "590501001",
        "address":           "Пермский край, г. Пермь, ш. Космонавтов, д. 111И, к. 1, помещ. 77",
        "signatory":         "Некрасова Артёма Владимировича",
        "signatory_short":   "Некрасов А.В.",
        "position":          "исполнительного директора",
        "authority":         "Доверенности № 6 от 04.04.2025 г.",
        "bank_account":      "40702810649770000811",
        "bank_name":         "ВОЛГО-ВЯТСКИЙ БАНК ПАО СБЕРБАНК",
        "bank_corr_account": "30101810900000000603",
        "bank_bik":          "042202603",
        "phone":             "+7 (919) 450-18-34",
    }
}

result = assemble(data, template_path="template.docx")
print(f"✅ Готово: {result}")
