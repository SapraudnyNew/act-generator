"""
test_run.py — тестовый прогон на счёт-договоре №1128 (Нотамедиа)
"""
from assembler import assemble

data = {
    "invoice_number":    "1128",
    "invoice_date":      "16.02.2026",
    "act_date":          "23.03.2026",
    "service_name":      "консультационные услуги по теме «Маркетинг ключевых клиентов»",
    "hours":             15,
    "hours_text":        "пятнадцать",
    "rate":              6600,
    "total_amount":      "99 000,00",
    "total_amount_text": "Девяносто девять тысяч",
    "currency":          "RUB",
    "payment_link":      "https://read.paperflite.com/collections/69a13888b480446d80a2f659",
    "client": {
        "name":              "ООО «НОТАМЕДИА»",
        "inn":               "7715515265",
        "kpp":               "771701001",
        "address":           "129085, город Москва, вн.тер. г. муниципальный округ Останкинский, пр-кт Мира, дом 101, строение 2, помещение 1/1",
        "signatory":         "Малышева Максима Вадимовича",
        "position":          "генерального директора",
        "bank_account":      "40702810301100001836",
        "bank_name":         "АО «АЛЬФА-БАНК» г. Москва",
        "bank_corr_account": "30101810200000000593",
        "bank_bik":          "044525593",
        "phone":             "(495) 995-15-21",
    }
}

result = assemble(data, template_path="template.docx", output_path="act_1128_test.docx")
print(f"✅ Готово: {result}")
