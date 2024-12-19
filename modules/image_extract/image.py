import os
from pypdf import PdfReader

def remove_duplicate_lines(text_output_path, seen):
    """
    对指定的文本文件按换行符 \n 分割后的行进行去重。
    :param text_output_path: 文本文件路径
    """
    #用来存储已经出现过的行
    
    unique_lines = []

    #读取文件内容
    with open(text_output_path, "r", encoding="utf-8") as file:
        content = file.read()

    #以 \n 为分隔符，按行去重
    for line in content.split("\n"):
        if line not in seen:
            unique_lines.append(line)
            seen.append(line)

    # 将去重后的内容重新写入文件，并重新加入换行符
    with open(text_output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(unique_lines) + "\n")
    
def text_and_image_extract(input_dir, output_dir):
    """
    从指定的输入目录中的所有 PDF 文件中，提取包含图片的页面及其上一页的文本内容，
    并保存为以图片名称命名的 .txt 文件。
    同时删除页眉页尾，并将所有内容合并为一行，段落换行转换为 /n。
    """
    # 遍历输入目录中的所有 PDF 文件
    seen = []
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

            # 遍历每一页，并提取图片和文本
            for page_num, page in enumerate(reader.pages, start=1):
                if hasattr(page, 'images') and page.images:
                    for image in page.images:
                        # 保存提取的图片到输出目录
                        image_path = os.path.join(pdf_output_dir, image.name)
                        with open(image_path, "wb") as fp:
                            fp.write(image.data)

                        print(f"保存图片 {image.name} 到 {image_path}（来自 {pdf_file} 第 {page_num} 页）")

                        # 提取当前页的文本内容
                        current_page_text = page.extract_text()

                        # 提取上一页的文本内容
                        if page_num > 1:
                            previous_page_text = reader.pages[page_num - 2].extract_text()
                        else:
                            previous_page_text = ""

                        # 合并上一页和当前页的文本
                        full_text = previous_page_text + "\n" + current_page_text

                        # 删除页眉和页尾
                        #cleaned_text = remove_header_footer(full_text)

                        # 将段落中的换行符替换为 /n，并将所有内容合并为一行
                        #single_line_text = '/n'.join(line.strip() for line in full_text.splitlines() if line.strip())

                        # 获取图片文件名的主体部分（去除扩展名）
                        image_name_without_ext = os.path.splitext(image.name)[0]

                        # 将处理后的文本内容保存到以图片名称命名的 .txt 文件
                        text_output_path = os.path.join(pdf_output_dir, f"{image_name_without_ext}.txt")
                        with open(text_output_path, "w", encoding="utf-8") as text_file:
                            text_file.write(full_text)

                        print(f"保存处理后的文本内容到 {text_output_path}")
                        remove_duplicate_lines(text_output_path, seen)
                        print(f"去除 {text_output_path} 文件中的重复行")


        
# 调用函数示例
input_dir = '/home/xylv/dataset/fabpdf/extracted/sliced/ye'
output_dir = '/home/xylv/dataset/fabpdf/results_divide/ye'
text_and_image_extract(input_dir, output_dir)
