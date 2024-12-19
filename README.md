
# Dataset Generation Toolkit

## 功能简介

本工具集支持将 PDF 和 Word 文件转换为 JSON 格式，并支持手写体和文本图像的处理。

### 核心功能

- **PDF/Word 转 JSON**  
  使用脚本生成带有图片说明的 JSON 文件。

- **OCR 处理**  
  `paddle_OCR.py` 专为处理手写或文本图像设计。

- **文档结构调整**  
  去除 PDF 页眉页脚并返回调整后的页面边界。

---

## 模块详解

### 1. 文件转换
- **`./module/pdf2`**  
  将 PDF 文件转换为 Word 或 TXT 文件。  
  （建议使用 Adobe API 以获得更优质的 Word 文件。）

### 2. 关键词提取
- **`./module/keyword`**  
  根据 `keyword.txt` 文件提取文档中的关键信息。

### 3. 页眉页脚移除
- **`./module/divide`**  
  去除 PDF 文件中的页眉和页脚内容，返回调整后的页面边界。
  
---
## 使用指南

###** 1. OCR 识别**
运行以下命令，适用于手写和扫描文本的处理：
```bash
python paddle_OCR.py

### **2.文档处理与转换**
将 PDF 转换为 Word 或 TXT 格式
```bash
python ./modules/pdf2/pdf2doc.py
```bash
python ./modules/pdf2/pdf2text.py
```bash
python ./modules/pdf2/pdf2txt.py
页眉页脚移除在./module/divide下

### **3.json生成**
生成 JSON
使用 text_generation.py 脚本将文档转换为包含图片说明的 JSON 文件：
```bash
python ./text_generation.py 
使用 multi_conversation_imgsummary.py 脚本生成包含图片说明的 JSON 文件：
```bash
python ./multi_conversation_imgsummary.py -


###4.可以修改utils中的内容生成qa问答等。
