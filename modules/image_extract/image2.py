import os
from pypdf import PdfReader
import re

def remove_specified_content(text_output_path, words_to_remove):
    """
    从 txt 文件中移除指定的文字内容。
    
    :param text_output_path: 输入的 txt 文件路径
    :param words_to_remove: 需要移除的文字列表
    """
    pattern = '|'.join(re.escape(sub) for sub in words_to_remove)
    
    with open(text_output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除指定词语
    content = re.sub(pattern, '', content)

    # 将处理后的内容写入同一文件
    with open(text_output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已处理并保存到 {text_output_path}")
    return content

def replace_repeated_dots(content, replace_char):
    """
    替换连续重复2次以上的字符为指定字符。
    
    :param content: 文本内容
    :param replace_char: 替换字符
    """
    content = content.replace(" .", ".")
    pattern = r'(\.{3,})'
    return re.sub(pattern, replace_char, content)

def convert_to_single_line(text_output_path, replace_char):
    """
    将文本数据转换为一行，换行符用 \n 代替，并替换连续的点为 'page'。
    
    :param text_output_path: 文本文件路径
    :param replace_char: 替换连续点的字符
    """
    with open(text_output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 将换行符替换为 \n，并合并为一行
    single_line_text = content.replace('\n', '\\n')

    # 替换连续的点
    single_line_text = replace_repeated_dots(single_line_text, replace_char)

    # 将合并后的内容写回文件
    with open(text_output_path, 'w', encoding='utf-8') as f:
        f.write(single_line_text)

    print(f"文本内容已转换为一行，并保存至 {text_output_path}")

def text_and_image_extract(input_dir, output_dir, words_to_remove, replace_char):
    """
    从 PDF 文件中提取包含图片的页面及其上一页的文本，并保存文本和图片。
    同时处理文本中的页眉页脚，段落换行转换为 \n。
    """
    seen = []
    for pdf_file in os.listdir(input_dir):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, pdf_file)

            # 创建输出目录
            pdf_output_dir = os.path.join(output_dir, os.path.splitext(pdf_file)[0])
            os.makedirs(pdf_output_dir, exist_ok=True)

            reader = PdfReader(pdf_path)

            for page_num, page in enumerate(reader.pages, start=1):
                if hasattr(page, 'images') and page.images:
                    for image in page.images:
                        image_path = os.path.join(pdf_output_dir, image.name)
                        with open(image_path, "wb") as fp:
                            fp.write(image.data)
                        print(f"保存图片 {image.name} 到 {image_path}（来自 {pdf_file} 第 {page_num} 页）")

                        current_page_text = page.extract_text() or ""

                        # 提取上一页的文本内容
                        previous_page_text = reader.pages[page_num - 2].extract_text() if page_num > 1 else ""

                        full_text = previous_page_text + "\n" + current_page_text

                        image_name_without_ext = os.path.splitext(image.name)[0]
                        text_output_path = os.path.join(pdf_output_dir, f"{image_name_without_ext}.txt")

                        with open(text_output_path, "w", encoding="utf-8") as text_file:
                            text_file.write(full_text)

                        print(f"保存处理后的文本内容到 {text_output_path}")

                        # 处理文本：移除指定词、转换为单行、去除重复字符
                        remove_specified_content(text_output_path, words_to_remove)
                        convert_to_single_line(text_output_path, replace_char)




# 调用函数示例
input_dir = '/home/xylv/dataset/fabpdf/extracted/sliced/ye'
output_dir = '/home/xylv/dataset/fabpdf/results_divide/ye'
#words_to_remove = [""]
words_to_remove = ['Note - Viewing', "PDF files within a web browser", "Use HTML for full navigation", "User’s Manual", "User’s and Reference Manual", "v2021", " © 2021.", "Tachyon LMC+ User Guide for","Tachyon FEM+ User Guide for" ,"Tachyon OPC+ User Guide for ", "User Guide for the TAC GUI",]
replace_char = " page"

text_and_image_extract(input_dir, output_dir, words_to_remove, replace_char)
