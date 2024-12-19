import json
import os
import re
import pdfplumber
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    pdf_text = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                # 按段落分隔文本并转换为一行
                paragraphs = [p.strip().replace('\n', ' ') for p in re.split(r'\n{2,}', page_text.strip()) if p.strip()]
                pdf_text[f'page_{i + 1}'] = paragraphs
                
    return pdf_text

def extract_table_from_pdf(pdf_path):
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            for table_num, table in enumerate(page.extract_tables()):
                # 将表格内容转换为 JSON 格式
                table_json = [{'columns': row} for row in table]
                tables.append({
                    'page': i + 1,
                    'table': table_num + 1,
                    'content': table_json
                })
                
    return tables

def save_to_json(pdf_text, tables, output_path):
    result = {'pages': [], 'tables': tables}
    
    for page_num, paragraphs in pdf_text.items():
        page_content = {'page': page_num, 'content': []}
        for paragraph in paragraphs:
            page_content['content'].append({'type': 'text', 'content': paragraph})
        
        # 插入表格内容
        for table in tables:
            if table['page'] == int(page_num.split('_')[1]):
                page_content['content'].append({'type': 'table', 'content': table['content']})
        
        result['pages'].append(page_content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def main(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.pdf', '.json'))
            
            print(f'Processing {pdf_path}...')
            pdf_text = extract_text_from_pdf(pdf_path)
            tables = extract_table_from_pdf(pdf_path)
            save_to_json(pdf_text, tables, output_path)
            print(f'Saved JSON to {output_path}')

# 使用示例
input_dir = '/home/xylv/dataset/fabpdf/extracted/sliced/ye'
output_dir = '/home/xylv/dataset/fabpdf/results_divided/results_dividedjson'
main(input_dir, output_dir)
