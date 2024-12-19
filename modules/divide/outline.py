import PyPDF2
import re

# 加载关键词
def load_keywords(keyword_file_path):
    with open(keyword_file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

# 从PDF目录中获取页码
def extract_toc_with_pages(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    outline = reader.outline  # 提取PDF目录
    toc = []

    for item in outline:
        if isinstance(item, list):
            for subitem in item:
                if isinstance(subitem, PyPDF2.generic.Destination):
                    toc.append((subitem.title, subitem.page_number))
        elif isinstance(item, PyPDF2.generic.Destination):
            toc.append((item.title, item.page_number))
    
    return toc

# 在目录中搜索关键词
def search_keywords_in_toc(toc, keywords):
    matched_items = []

    for title, page in toc:
        if any(re.search(keyword, title, re.IGNORECASE) for keyword in keywords):
            matched_items.append((title, page))
    
    return matched_items

# 主函数，执行搜索并打印匹配项
def extract_pages_from_toc_by_keywords(input_pdf_path, keyword_file_path):
    keywords = load_keywords(keyword_file_path)
    toc = extract_toc_with_pages(input_pdf_path)
    
    if not toc:
        print("未找到PDF目录")
        return
    
    matched_items = search_keywords_in_toc(toc, keywords)

    if matched_items:
        print("匹配到的内容和页码如下：")
        for title, page in matched_items:
            print(f"内容: {title}，页码: {page}")
    else:
        print("未找到匹配的关键词")

if __name__ == '__main__':
    input_pdf_path = '/home/xylv/dataset/fabpdf/fab_pdf/userguide/your_pdf_file.pdf'
    keyword_file_path = '/home/xylv/python_code/dataset_extract/modules/divide/keyword.txt'
    
    extract_pages_from_toc_by_keywords(input_pdf_path, keyword_file_path)
