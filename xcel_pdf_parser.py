from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

bill = r'C:\Users\NicholasRolstad\Downloads\HomeEnergyReport.pdf'
text_list = []
for page_layout in extract_pages(bill):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            text_list.append(element.get_text())
            
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

idx = 0
for item in text_list:
    if item.split()[0] in months:# in months:
        print(item.split()[0], ':', text_list[idx+47])
    idx += 1