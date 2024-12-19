from PyPDF2 import PdfReader, PdfWriter
import os

def remove_header_footer(input_pdf_path, output_pdf_path):
    # 读取PDF文件
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]

        # 获取页面的宽高
        width = page.mediabox.width
        height = page.mediabox.height

        # 调整页面的媒体框，以去除上下的页眉和页脚
        page.mediabox.lower_left = (0, 64)  # 从下60单位开始，去除底部页脚
        page.mediabox.upper_right = (width, height - 64)  # 到上60单位结束，去除顶部页眉

        # 将修改后的页面添加到writer
        writer.add_page(page)

    # 保存处理后的PDF
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)


# PDF文件路径
input_directory = "/home/xylv/dataset/fabpdf/extracted/ye"
output_directory = "/home/xylv/dataset/fabpdf/extracted/sliced/ye"

# 确保输出目录存在
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# 遍历输入目录中的所有PDF文件
for filename in os.listdir(input_directory):
    if filename.endswith(".pdf"):
        input_pdf_path = os.path.join(input_directory, filename)
        output_pdf_path = os.path.join(output_directory, filename)
        remove_header_footer(input_pdf_path, output_pdf_path)

print("PDF处理完成。")
