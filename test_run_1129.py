"""
test_run_1129.py — тестовый прогон на счёт-договоре №1129 (Клининг 911)
"""
from assembler import assemble

data = {
    "invoice_number":    "1129",
    "invoice_date":      "18.02.2026",
    "act_date":          "23.03.2026",
    "service_name":      "консультационные услуги по теме «Маркетинг ключевых клиентов»",
    "hours":             15,
    "hours_text":        "пятнадцать",
    "rate":              5666.67,
    "total_amount":      "85 000,00",
    "total_amount_text": "Восемьдесят пять тысяч",
    "currency":          "RUB",
    "payment_link":      "https://read.paperflite.com/collections/69a138c781372d5611f43ad2",
    "client": {
        "name":              "ООО «Клининг 911»",
        "inn":               "6731071625",
        "kpp":               "6731010011",
        "address":           "214036, г. Смоленск, ул. Попова, д. 120, кв. 132",
        "signatory":         "Мартынов Дмитрий Сергеевич",
        "position":          "директора",
        "bank_account":      "40702810359190005841",
        "bank_name":         "Смоленское ОСБ № 8609",
        "bank_corr_account": "30101810000000000632",
        "bank_bik":          "046614632",
        "phone":             "",
    }
}

result = assemble(data, template_path="template.docx", output_path="act_1129_test.docx")
print(f"✅ Готово: {result}")
