import os
from pypdf import PdfReader

def text_for_image_pages_extract(input_dir, output_dir):
    """
    从指定的输入目录中的所有 PDF 文件中，提取包含图片页及其上一页的文本内容，
    并保存到指定的输出目录，同时删除文件中的相同行，将段落换行转换为 /n 并转化为一行。
    """
    # 遍历输入目录中的所有 PDF 文件
    for pdf_file in os.listdir(input_dir):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, pdf_file)

            # 使用 PDF 文件名作为输出文件夹名
            pdf_output_dir = os.path.join(output_dir, os.path.splitext(pdf_file)[0])

            # 检查并创建每个 PDF 对应的输出文件夹
            if not os.path.exists(pdf_output_dir):
                os.makedirs(pdf_output_dir)

            # 读取 PDF 文件
            reader = PdfReader(pdf_path)

            # 遍历每一页，并提取包含图片页及上一页的文本
            for page_num, page in enumerate(reader.pages, start=1):
                if hasattr(page, 'images') and page.images:
                    # 提取当前页的文本内容
                    current_page_text = page.extract_text()

                    # 提取上一页的文本内容
                    if page_num > 1:
                        previous_page_text = reader.pages[page_num - 2].extract_text()
                    else:
                        previous_page_text = ""

                    # 将上一页和当前页的文本内容保存到 txt 文件
                    text_output_path = os.path.join(pdf_output_dir, f"page_{page_num}_text.txt")
                    with open(text_output_path, "w", encoding="utf-8") as text_file:
                        text_file.write(previous_page_text)
                        text_file.write(current_page_text)

                    print(f"保存包含图片的页和上一页的文本内容到 {text_output_path}")

                    # 读取刚刚保存的 txt 文件，删除相同行并合并为一行
                    with open(text_output_path, "r", encoding="utf-8") as file:
                        lines = file.readlines()

                    # 删除重复的行
                    unique_lines = list(dict.fromkeys(lines))

                    # 将段落中的换行符替换为 "/n"，并将所有内容合并为一行
                    single_line_text = '/n'.join(line.strip() for line in unique_lines if line.strip())

                    # 将处理后的内容重新写回到 txt 文件中
                    with open(text_output_path, "w", encoding="utf-8") as file:
                        file.write(single_line_text)

                    print(f"更新后的文本内容已保存到 {text_output_path}")

# 调用函数示例
input_dir = '/home/xylv/dataset/fabpdf/extracted/flow'
output_dir = '/home/xylv/dataset/fabpdf/results_divide/txt/flow'
text_for_image_pages_extract(input_dir, output_dir)
