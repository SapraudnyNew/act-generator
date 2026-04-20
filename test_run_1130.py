"""
test_run_1130.py — тестовый прогон на счёт-договоре №1130 (Ласмарт)
Файл сохранится как: «Акт к Счет-договору № 1130 от 24.02.2026г.docx»
"""
from assembler import assemble

data = {
    "invoice_number":    "1130",
    "invoice_date":      "24.02.2026",
    "act_date":          "23.03.2026",
    "service_name":      "консультационные услуги по теме «Маркетинг ключевых клиентов»",
    "hours":             15,
    "hours_text":        "пятнадцать",
    "rate":              13200,
    "total_amount":      "198 000,00",
    "total_amount_text": "Сто девяносто восемь тысяч",
    "currency":          "RUB",
    "payment_link":      "https://read.paperflite.com/collections/69a1391d5041d136e4471bc6",
    "client": {
        "name":              "ООО «Ласмарт»",
        "inn":               "7814186283",
        "kpp":               "781401001",
        "address":           "197371, Санкт-Петербург, ул. Долгоозерная, д. 33, к. 2, кв. 167",
        "signatory":         "Лаврова Антона Алексеевича",
        "signatory_short":   "Лавров А.А.",
        "position":          "генерального директора",
        "bank_account":      "40702810635260000075",
        "bank_name":         "Филиал «Центральный» Банка ВТБ (ПАО)",
        "bank_corr_account": "30101810145250000411",
        "bank_bik":          "044525411",
        "phone":             "8 800 100 77 52",
    }
}

result = assemble(data, template_path="template.docx")
print(f"✅ Готово: {result}")
