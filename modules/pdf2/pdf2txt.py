import os
import re
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

# 解析单个PDF文件并转换为TXT文件
def onePdfToTxt(filepath, outpath):
    try:
        with open(filepath, 'rb') as fp, open(outpath, 'w', encoding='utf-8') as outfp:
            parser = PDFParser(fp)
            doc = PDFDocument(parser)
            if not doc.is_extractable:
                pass
            else:
                resource = PDFResourceManager()
                laparams = LAParams()
                device = PDFPageAggregator(resource, laparams=laparams)
                interpreter = PDFPageInterpreter(resource, device)
                for page in enumerate(PDFPage.create_pages(doc)):
                    interpreter.process_page(page[1])
                    layout = device.get_result()
                    for out in layout:
                        if hasattr(out, "get_text"):
                            text = out.get_text()
                            outfp.write(text + '\n')
    except Exception as e:
        print(e)

# 处理目录下的所有PDF文件
def manyPdfToTxt(fileDir, resultDir):
    for root, dirs, files in os.walk(fileDir):
        for file in files:
            if file.lower().endswith('.pdf'):
                filePath = os.path.join(root, file)
                relativePath = os.path.relpath(root, fileDir)
                outputDir = os.path.join(resultDir, relativePath)
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)
                outPath = os.path.join(outputDir, re.sub(r'\.pdf', '', file, flags=re.I) + '.txt')
                onePdfToTxt(filePath, outPath)
                print(f"Saved in {outPath}")

# 使用示例
pdf_directory = '/home/xylv/dataset/fabpdf/fab_pdf'  # PDF文件的根目录
output_directory = '/home/xylv/dataset/fabpdf/result_txt'  # 结果保存的根目录

manyPdfToTxt(pdf_directory, output_directory)
