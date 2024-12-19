import fitz
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
import os

def remove_header_footer(pdf_path):
    """
    从 PDF 文件中去除页眉和页脚，并返回调整后的页面边界。
    :param pdf_path: PDF 文件的路径
    :return: 调整后的页面边界 (x_min, y_min, x_max, y_max)
    """
    # Load the document using PyMuPDF (fitz)
    document = fitz.open(pdf_path)
    n_pages = document.page_count
    
    if n_pages == 1:
        # 如果只有一页，可以选择是否插入文件或其他处理方式
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
    quantile = 0.25
    
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
    std = 1  # Assuming headers/footers have near-zero standard deviation
    
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
    
    return x_min, y_min, x_max, y_max

def process_pdfs(input_dir, output_dir):
    """
    从指定目录下的所有 PDF 文件中去除页眉和页脚，并保存处理后的 PDF 文件。
    :param input_dir: 输入 PDF 文件所在目录
    :param output_dir: 处理后 PDF 文件的保存目录
    """
    # 遍历目录中的所有 PDF 文件
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file_name)
            output_pdf_path = os.path.join(output_dir, file_name)

            x_min, y_min, x_max, y_max = remove_header_footer(pdf_path)
            
            # Open the original PDF
            document = fitz.open(pdf_path)
            
            # Create a new PDF for saving processed content
            new_document = fitz.open()
            
            # Process each page
            for page in document:
                # Define the crop box for each page to exclude header and footer
                rect = fitz.Rect(x_min, y_min, x_max, y_max)
                page.set_cropbox(rect)
                
                # Add the page to the new document
                new_document.insert_pdf(document, from_page=page.number, to_page=page.number)
            
            # Save the new PDF
            new_document.save(output_pdf_path)
            new_document.close()
            document.close()
            print(f"处理完毕: {file_name}")

# 调用函数示例
input_dir = '/home/xylv/dataset/fabpdf/extracted/ye'
output_dir = '/home/xylv/dataset/fabpdf/fab_pdf/YE'
process_pdfs(input_dir, output_dir)
