"""
test_run_1132.py — ИП Самтенко Александр Владимирович, счёт-договор №1132

Правило для ИП:
  - authority оставлять пустым (фраза «действующего на основании...» не нужна)
  - КПП отсутствует
  - В шапке: «именуемый в дальнейшем» (мужской род для ИП-физлица)
"""
from assembler import assemble

data = {
    "invoice_number":    "1132",
    "invoice_date":      "27.02.2026",
    "act_date":          "23.03.2026",
    "service_name":      "консультационные услуги по теме «Маркетинг ключевых клиентов»",
    "hours":             15,
    "hours_text":        "пятнадцать",
    "rate":              6600,
    "total_amount":      "99 000,00",
    "total_amount_text": "Девяносто девять тысяч",
    "currency":          "RUB",
    "payment_link":      "https://read.paperflite.com/collections/69a13967768b173bd41cd97c",
    "client": {
        "name":              "ИП Самтенко Александр Владимирович",
        "inn":               "504013520978",
        "kpp":               "",
        "address":           "140155, Московская обл., г. Раменское, с. Речицы, ул. Радужная, д. 87",
        "signatory":         "Самтенко Александра Владимировича",
        "signatory_short":   "Самтенко А.В.",
        "position":          "индивидуального предпринимателя",
        "authority":         "",
        "bank_account":      "40802810620000407791",
        "bank_name":         "ООО «Банк Точка»",
        "bank_corr_account": "30101810745374525104",
        "bank_bik":          "044525104",
        "phone":             "+7 926 482-33-57",
    }
}

result = assemble(data, template_path="template.docx")
print(f"✅ Готово: {result}")
