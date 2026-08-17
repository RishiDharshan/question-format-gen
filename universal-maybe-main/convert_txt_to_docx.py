import docx
from doc_maker import _add_content_with_tables, clean_xml
import re

txt_file = 'outputs/ssc_sample_output_249645.txt'
with open(txt_file, 'r') as f:
    text = f.read()

pattern = r"(\*\*|__)(.*?)\1"
clean_text = re.sub(pattern, r"\2", text)

doc = docx.Document()
_add_content_with_tables(doc, clean_xml(clean_text))
doc.save('outputs/ssc_sample_output_249645.docx')
print("Successfully saved to outputs/ssc_sample_output_249645.docx")
