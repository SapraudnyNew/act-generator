"""
create_template.py

Генерирует template.docx на основе реальной структуры акта сдачи-приёмки услуг.

Запуск:
    python create_template.py
Результат: template.docx в текущей директории.
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy


def set_cell_border(cell, **kwargs):
    """Устанавливает границы ячейки таблицы."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        val = kwargs.get(edge)
        if val:
            border = OxmlElement(f'w:{edge}')
            border.set(qn('w:val'), val.get('val', 'single'))
            border.set(qn('w:sz'), str(val.get('sz', 4)))
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), val.get('color', '000000'))
            tcBorders.append(border)
    tcPr.append(tcBorders)


def add_paragraph(doc, text='', bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT,
                  space_before=0, space_after=6, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.alignment = align
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(size)
    return p


def make_template():
    doc = Document()

    # Поля страницы
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)

    # Заголовок
    p = add_paragraph(doc,
        'Акт сдачи-приёмки услуг к Счет-договору № {{invoice_number}} от {{invoice_date}}г.',
        bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

    # Город и дата
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(10)
    # город слева, дата справа — через табуляцию
    run_city = p2.add_run('г. Москва')
    run_city.font.size = Pt(11)
    # Таб до даты
    tab = p2.add_run('\t')
    run_date = p2.add_run('{{act_date}}г.')
    run_date.font.size = Pt(11)
    p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Настройка табуляции (дата по правому краю)
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    pPr = p2._p.get_or_add_pPr()
    tabs = OxmlElement('w:tabs')
    tab_el = OxmlElement('w:tab')
    tab_el.set(qn('w:val'), 'right')
    tab_el.set(qn('w:pos'), '9072')  # ~16 см
    tabs.append(tab_el)
    pPr.append(tabs)

    # Вводный абзац — стороны
    intro = (
        '{{contractor.name}}, именуемое в дальнейшем «Исполнитель», '
        'в лице {{contractor.position}} {{contractor.signatory}}, '
        'действующего на основании Устава, с одной стороны, '
        'и {{client.name}}, именуемое в дальнейшем «Заказчик», '
        'в лице {{client.position}} {{client.signatory}}, '
        'действующего на основании Устава, с другой стороны, '
        'вместе и по отдельности именуемые «Стороны», составили настоящий акт '
        'сдачи-приёмки услуг к Счет-договору № {{invoice_number}} '
        'от {{invoice_date}}г. (далее – Акт):'
    )
    add_paragraph(doc, intro, size=11, space_before=0, space_after=8)

    # Пункт 1
    add_paragraph(doc,
        '1. Исполнитель оказал {{service_name}} – {{hours}} ({{hours_text}}) часов.',
        size=11, space_after=6)

    # Пункт 2
    add_paragraph(doc,
        '2. Сумма оказанных услуг составила {{total_amount}} ({{total_amount_text}} рублей), 00 коп. '
        'НДС не облагается на основании применения Исполнителем упрощенной системы '
        'налогообложения в соответствии со ст. 346.12, 346.13 Главы 26.2 '
        'Налогового кодекса Российской Федерации.',
        size=11, space_after=6)

    # Пункт 3
    add_paragraph(doc,
        '3. Материалы сессий доступны по ссылке {{payment_link}}',
        size=11, space_after=6)

    # Пункт 4
    add_paragraph(doc,
        '4. Консалтинговые услуги по Счет-договору № {{invoice_number}} '
        'от {{invoice_date}}г. выполнены полностью и в срок. '
        'Претензий по объему, качеству результата работ и срокам '
        'их выполнения Заказчик не имеет.',
        size=11, space_after=6)

    # Пункт 5
    add_paragraph(doc,
        '5. Акт составлен в двух экземплярах, по одному для каждой из сторон.',
        size=11, space_after=14)

    # -------------------------------------------------------------------
    # Таблица реквизитов (исполнитель | заказчик)
    # -------------------------------------------------------------------
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    tbl.autofit = False
    tbl.columns[0].width = Cm(8.5)
    tbl.columns[1].width = Cm(8.5)

    def fill_party(cell, role, prefix):
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        lines = [
            (f'{role}:', True),
            (f'{{{{prefix}}.name}}'.replace('prefix', prefix), False),
            (f'ИНН {{{{prefix}}.inn}}'.replace('prefix', prefix), False),
            (f'КПП {{{{prefix}}.kpp}}'.replace('prefix', prefix), False),
            (f'{{{{prefix}}.address}}'.replace('prefix', prefix), False),
            ('', False),
            ('Банковские реквизиты:', True),
            (f'р/с {{{{prefix}}.bank_account}}'.replace('prefix', prefix), False),
            (f'{{{{prefix}}.bank_name}}'.replace('prefix', prefix), False),
            (f'к/с {{{{prefix}}.bank_corr_account}}'.replace('prefix', prefix), False),
            (f'БИК {{{{prefix}}.bank_bik}}'.replace('prefix', prefix), False),
            (f'Тел. {{{{prefix}}.phone}}'.replace('prefix', prefix), False),
        ]
        for i, (text, bold) in enumerate(lines):
            if i == 0:
                p = cell.paragraphs[0]
            else:
                p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(text)
            run.bold = bold
            run.font.size = Pt(10)

    fill_party(tbl.rows[0].cells[0], 'Исполнитель', 'contractor')
    fill_party(tbl.rows[0].cells[1], 'Заказчик', 'client')

    doc.add_paragraph()  # отступ

    # -------------------------------------------------------------------
    # Таблица подписей
    # -------------------------------------------------------------------
    sig_tbl = doc.add_table(rows=3, cols=2)
    sig_tbl.autofit = False
    sig_tbl.columns[0].width = Cm(8.5)
    sig_tbl.columns[1].width = Cm(8.5)

    def sig_cell(cell, text, bold=False):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(11)

    sig_cell(sig_tbl.rows[0].cells[0], 'Исполнитель', bold=True)
    sig_cell(sig_tbl.rows[0].cells[1], 'Заказчик', bold=True)
    sig_cell(sig_tbl.rows[1].cells[0], '{{contractor.position}}')
    sig_cell(sig_tbl.rows[1].cells[1], '{{client.position}}')
    sig_cell(sig_tbl.rows[2].cells[0], 'Подпись _________________ / {{contractor.signatory}} /  М.П.')
    sig_cell(sig_tbl.rows[2].cells[1], 'Подпись _________________ / {{client.signatory}} /  М.П.')

    # Убираем границы у таблицы подписей
    from docx.oxml.ns import qn
    for row in sig_tbl.rows:
        for cell in row.cells:
            set_cell_border(cell,
                top={'val': 'none'},
                bottom={'val': 'none'},
                left={'val': 'none'},
                right={'val': 'none'},
            )

    doc.save('template.docx')
    print('✅ template.docx создан')


if __name__ == '__main__':
    make_template()
