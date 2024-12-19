import os
from pdf2docx import Converter

# 转换单个PDF文件为Word文件
def onePdfToWord(pdf_file, word_file):
    cv = Converter(pdf_file)
    cv.convert(word_file, start=0, end=None)  # start=0表示从第一页开始, end=None表示到最后一页
    cv.close()

# 批量转换PDF文件为Word文件
def manyPdfToWord(fileDir, resultDir):
    for root, dirs, files in os.walk(fileDir):
        for file in files:
            if file.lower().endswith('.pdf'):
                filePath = os.path.join(root, file)
                relativePath = os.path.relpath(root, fileDir)
                outputDir = os.path.join(resultDir, relativePath)
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)
                word_file = os.path.join(outputDir, os.path.splitext(file)[0] + '.docx')
                onePdfToWord(filePath, word_file)
                print(f"Saved in {word_file}")

# 使用示例
pdf_directory = '/home/xylv/dataset/fabpdf/fab_pdf'  # PDF文件的根目录
output_directory = '/home/xylv/dataset/fabpdf/result_docx'  # 结果保存的根目录

manyPdfToWord(pdf_directory, output_directory)
