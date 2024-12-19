# -*- coding: utf-8 -*-
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
import sys
from utils import prompt
from utils.prompt import prompt_datasetgeneration, prompt_class_questions_cause
import os
import json  # 导入 json 模块
from PIL import Image
sys.path.append('/home/xylv/python_code/dataset_extract')
image_directory = "/home/xylv/dataset/fab"

# 获取目录下的所有图片文件名（你可以根据图片格式进行筛选，如jpg, png, etc.）
images = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
model_dir = "/home/xylv/.cache/modelscope/hub/qwen/Qwen2-VL-2B-Instruct"

# Load the model on the available device(s)
model = Qwen2VLForConditionalGeneration.from_pretrained(
     model_dir,
     torch_dtype="auto",
     device_map="auto",
)

# Default processor
processor = AutoProcessor.from_pretrained(model_dir)
promptdatasetgeneration = prompt.prompt_datasetgeneration
promptcause = prompt.prompt_class_questions_cause

# 创建一个字典来存储所有问题和答案
results = {}

for image in images:
    image_path = os.path.join(image_directory, image)
    print(f"正在处理图片: {image_path}")  # 打印图片路径

    # 第一轮对话
    messages = []
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": image_path,  # 处理单张图片
            },
            {
                "type": "text",
                "text": promptcause  # 第一轮问题
            },
        ],
    })

    # Preparation for inference for the first round
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")

    # Inference: Generation of the output for the first round
    generated_ids = model.generate(**inputs, max_new_tokens=2056)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    print(f"第一轮答案: {output_text[0]}")

    # 将问题和答案添加到结果字典中
    results[image] = {
        "questions": [output_text[0]]
    }

    # 第二轮对话
    messages = []
    messages.append({"role": "assistant", "content": output_text[0]})
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": image_path,  # 处理同一张图片
            },
            {
                "type": "text",
                "text": promptdatasetgeneration  # 第二轮问题
            },
        ],
    })

    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")

    # Inference: Generation of the output for the second round
    generated_ids = model.generate(**inputs, max_new_tokens=2056)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text1 = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    print(f"第二轮答案: {output_text1[0]}")

    # 将第二轮答案添加到结果字典中
    results[image]["answers"].append(output_text1[0])

# 将结果写入 JSON 文件
output_file = "/home/xylv/python_code/dataset_extract/results/jyq/output_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"结果已保存到 {output_file}")
