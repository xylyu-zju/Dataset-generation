from paddleocr import PaddleOCR, draw_ocr
ocr = PaddleOCR(use_angle_cls=True, lang="en")  # need to run only once to download and load model into memory
img_path = '/data1/xdlu/LISA/OCR/OCR_ic.jpg'
result = ocr.ocr(img_path, cls=True)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)


#from PIL import Image
#result = result[0]
#image = Image.open(img_path).convert('RGB')
#boxes = [line[0] for line in result]
#txts = [line[1][0] for line in result]
#scores = [line[1][1] for line in result]
#im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
#im_show = Image.fromarray(im_show)
#im_show.save('result.jpg')