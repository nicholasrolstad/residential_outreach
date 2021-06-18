from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

bill = r'C:\Users\NicholasRolstad\Downloads\xcel_bill.pdf'
text_list = []
for page_layout in extract_pages(bill):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            text_list.append(element.get_text())
            
