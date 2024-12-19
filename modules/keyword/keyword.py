import pdfplumber
import PyPDF2
import re
import os
import fitz
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN

def remove_hf(pdf_path):
    # Load the document using PyMuPDF (fitz)
    document = fitz.open(pdf_path)
    # Count pages
    n_pages = document.page_count
    
    if n_pages == 1:
        pass  # 根据需要处理单页PDF
    
    # Extract the coordinates of each block (paragraph)
    coordinates = {'x0': [], 'y0': [], 'x1': [], 'y1': []}
    for page in document:
        blocks = page.get_text('blocks')
        for block in blocks:
            coordinates['x0'].append(block[0])
            coordinates['y0'].append(block[1])
            coordinates['x1'].append(block[2])
            coordinates['y1'].append(block[3])
    
    # Store the block coordinates in a dataframe
    df = pd.DataFrame(coordinates)
    
    # Header/footer threshold
    quantile = 0.15
    
    # Calculate upper and lower quantiles
    upper = np.floor(df['y0'].quantile(1 - quantile))
    lower = np.ceil(df['y1'].quantile(quantile))
    
    # Calculate box boundaries (including header and footer)
    x_min = np.floor(df['x0'].min())
    x_max = np.ceil(df['x1'].max())
    y_min = np.floor(df['y0'].min())
    y_max = np.ceil(df['y1'].max())
    
    # HEADER/FOOTER FREQUENCY
    hff = 0.8
    min_clust = int(np.floor(n_pages * hff))
    if min_clust < 2:
        min_clust = 2
    
    hdbscan = HDBSCAN(min_cluster_size=min_clust)
    df['clusters'] = hdbscan.fit_predict(df)
    
    # Group by clusters and compute statistics
    df_group = df.groupby('clusters').agg(
        avg_y0=('y0', 'mean'),
        avg_y1=('y1', 'mean'),
        std_y0=('y0', 'std'),
        std_y1=('y1', 'std'),
        max_y0=('y0', 'max'),
        max_y1=('y1', 'max'),
        min_y0=('y0', 'min'),
        min_y1=('y1', 'min'),
        cluster_size=('clusters', 'count'),
        avg_x0=('x0', 'mean')
    ).reset_index()
    
    df_group = df_group.sort_values(['avg_y0', 'avg_y1'], ascending=[True, True])
    
    # Detect header and footer based on clustering
    std = 0  # Assuming headers/footers have near-zero standard deviation
    
    footer = np.floor(
        df_group[
            (np.floor(df_group['std_y0']) == std) &
            (np.floor(df_group['std_y1']) == std) &
            (df_group['min_y0'] >= upper) &
            (df_group['cluster_size'] <= n_pages)
        ]['min_y0'].min()
    )
    
    header = np.ceil(
        df_group[
            (np.floor(df_group['std_y0']) == std) &
            (np.floor(df_group['std_y1']) == std) &
            (df_group['min_y1'] <= lower) &
            (df_group['cluster_size'] <= n_pages)
        ]['min_y1'].max()
    )
    
    # If there is a footer, exclude it
    if not pd.isnull(footer):
        y_max = footer
    
    # If there is a header, exclude it
    if not pd.isnull(header):
        y_min = header
    
    # Calculate box boundaries (excluding header and footer)
    return x_min, y_min, x_max, y_max


# 利用正则表达式查找关键词，并提取（跳过页眉和页脚）
def extract_keyword_pages(filename, keywords, crop_box):
    matched_pages = []
    x_min, y_min, x_max, y_max = crop_box
    
    with pdfplumber.open(filename) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            
            # 裁剪页面以排除页眉和页脚
            cropped_page = page.within_bbox((x_min, y_min, x_max, y_max))
            page_text = cropped_page.extract_text()
            
            if page_text and any(re.search(keyword, page_text, re.IGNORECASE) for keyword in keywords):
                print(f'关键词在 {filename} 的第 {i+1} 页被找到')
                matched_pages.append(i)
    
    return matched_pages

# 保存匹配的页到新的PDF
def save_matched_pages_to_pdf(input_pdf_path, output_pdf_path, matched_pages):
    pdf_writer = PyPDF2.PdfWriter()
    with open(input_pdf_path, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        for page_num in matched_pages:
            pdf_writer.add_page(reader.pages[page_num])
        with open(output_pdf_path, 'wb') as outfile:
            pdf_writer.write(outfile)
    print(f"保存匹配页到新文件: {output_pdf_path}")

# 从文件中读取关键词
def load_keywords(keyword_file_path):
    with open(keyword_file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

if __name__ == '__main__':
    keyword_file_path = '/home/xylv/python_code/dataset_extract/modules/divide/keywordye.txt'
    pdf_path = '/home/xylv/dataset/fabpdf/fab_pdf/YE/calbr_defclass_user.pdf'
    input_pdf_folder = '/home/xylv/dataset/fabpdf/fab_pdf/YE'
    output_pdf_folder = '/home/xylv/dataset/fabpdf/results_divided/results_dividedpdf/YE'

    # Ensure output directory exists
    if not os.path.exists(output_pdf_folder):
        os.makedirs(output_pdf_folder)

    keywords = load_keywords(keyword_file_path)
    
    for file_name in os.listdir(input_pdf_folder):
        if file_name.endswith('.pdf'):
            input_pdf_path = os.path.join(input_pdf_folder, file_name)
            
            try:
                # 检测并获取裁剪区域
                crop_box = remove_hf(input_pdf_path)
                print(f"裁剪区域 (x_min, y_min, x_max, y_max) for {file_name}: {crop_box}")
                
                # 提取匹配的页码
                matched_pages = extract_keyword_pages(input_pdf_path, keywords, crop_box)
                
                if matched_pages:
                    output_pdf_path = os.path.join(output_pdf_folder, f'{file_name}_matched.pdf')
                    save_matched_pages_to_pdf(input_pdf_path, output_pdf_path, matched_pages)
            except Exception as e:
                print(f"处理文件 {file_name} 时出错: {e}")
