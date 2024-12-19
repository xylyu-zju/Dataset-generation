# -*- coding: utf-8 -*-
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import json
import torch
import sys
from utils import prompt
from utils.prompt import prompt_generate_summary_for_image, prompt_text_declare
import os
sys.path.append('/home/xylv/python_code/dataset_extract')

image_directory = "/home/xylv/python_code/dataset_extract/resources"
#txt_directory = "/home/xylv/python_code/dataset_extract/resources/txt"
#summary_dir = "/home/xylv/python_code/dataset_extract/results"
model_dir = "/home/xylv/.cache/modelscope/hub/qwen/Qwen2-VL-2B-Instruct"
#image_directory = "/home/xylv/dataset/fabpdf/results_divided/results_dividedimage"


# default: Load the model on the available device(s)
#model = Qwen2VLForConditionalGeneration.from_pretrained(
    #model_dir, torch_dtype="auto", device_map="auto"
#)

# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
model = Qwen2VLForConditionalGeneration.from_pretrained(
     model_dir,
     #torch_dtype="auto",
     torch_dtype=torch.bfloat16,
     attn_implementation="flash_attention_2",
     device_map="auto",
 )

# default processer
#processor = AutoProcessor.from_pretrained(model_dir)

# The default range for the number of visual tokens per image in the model is 4-16384. You can set min_pixels and max_pixels according to your needs, such as a token count range of 256-1280, to balance speed and memory usage.
min_pixels = 256*28*28
max_pixels = 1280*28*28
processor = AutoProcessor.from_pretrained(model_dir, min_pixels=min_pixels, max_pixels=max_pixels)
images = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]


promptsummary = prompt.prompt_generate_summary_for_image
prompttext = prompt.prompt_text_declare
messages = []


# 创建 message
for image in images:
  message = {
    "role": "user",
    "content": [
        {
            "type": "image",
            "image": os.path.join(image_directory, image),  # 正确使用 os.path.join 来拼接路径
                #"/home/xylv//dataset/fabpdf/results_divided/results_dividedimage/11_272.png",
                #{}".format(os.path.join(image_directory, image)),  # 使用 format() 方法
                #"resized_height": 280,
                #"resized_width": 420,
        },
        {
            "type": "text",
            "text": "The Calibre® 3DSTACK application enables you to verify designs containing flip chips, Through Silicon Vias (TSVs), and other 2.5D and 3D-IC configurations. For an introduction to the Calibre 3DSTACK tool, view the following getting started video: Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11 3D-IC Description Language Usage Restrictions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16 Requirements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16 Documentation Conventions. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17 Overview Traditional ICs are self-contained and are verified at the chip-level using Calibre nmDRC, Calibre nmLVS, Calibre RVE, and Calibre DESIGNrev. 3D-ICs consist of multiple stacked chips with connectivity achieved through traces on an interposer or with special vias or bumps. The Calibre 3DSTACK tool verifies the interfaces between these chips, which may consist of black box IP. A cross-section of a 3D-IC is illustrated in Figure 1-1. The primary difference between a 2.5D and 3D-IC configuration is the use of a silicon interposer. A silicon interposer, as illustrated in Figure 1-2, electrically connects the pads between chips. These chips can either use TSVs (allowing for additional stacking), or may contain no TSVs (in which case the chips do not allow for additional stacking and are flip chips). 2.5D configurations use a silicon interposer, while 3D-IC configurations contain TSVs in active silicon that form a complete 3D stack. A TSV is a via that passes through the substrate of a chip or silicon interposer. Typically, in a chip containing TSVs, devices and metal layers are manufactured on one side of the chip (the front), while additional metal layers are manufactured on the other side of the chip (the back). The front metal layers are normally manufactured at a more advanced process node than the back metal layers. Small spheres of solder called micro bumps can be used to connect multiple chips together. Refer to Figure 1-1. Calibre 3DSTACK operates on these configurations by supplementing your existing Calibre verification flow. Your existing Calibre flow operates on each design independently, while Calibre 3DSTACK operates on the interfaces between designs. Designs are assembled according to instructions contained in a 3DSTACK rule file, which include offset values along the x and y axes, rotation angles, and magnification factors. For example, in Figure 1-2, two designs (chip1 and chip2) are to be assembled on a silicon interposer. To assemble the die stack, chip2 is shifted along the x-axis by x_offset and the interposer is rotated clockwise by 90 degrees. Figure 1-2 summarizes the necessary inputs and outputs to a 3DSTACK assembly operation."  # 使用从 prompt.py 导入的 prompt_generate_summary_for_image
        },
        {
            "type": "text",
            "text": prompttext  # 使用从 prompt.py 导入的 prompt_generate_summary_for_image
        },
    ],
}

# 将 message 添加到 messages 列表
messages.append(message)
# Preparation for inference
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

# Inference: Generation of the output
generated_ids = model.generate(**inputs, max_new_tokens=2046)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print("First round output:",output_text[0])


for image in images:
 messages.append({"role": "assistant", "content": output_text[0]}) 
 message = {
    "role": "user",
    "content": [
        {
            "type": "image",
            "image": os.path.join(image_directory, image),  # 正确使用 os.path.join 来拼接路径
                #"/home/xylv//dataset/fabpdf/results_divided/results_dividedimage/11_272.png",
                #{}".format(os.path.join(image_directory, image)),  # 使用 format() 方法
                #"resized_height": 280,
                #"resized_width": 420,
        },
        {
            "type": "text",
            "text": promptsummary  # 使用从 prompt.py 导入的 prompt_generate_summary_for_image
        },
    ],
}

messages.append(message)
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

generated_ids = model.generate(**inputs, max_new_tokens=2048)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text2 = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print("Second round output:",output_text2[0])

# The second round of dialogue.
messages.append({"role": "assistant", "content": output_text2[0]})
messages.append({"role": "user", "content": 'According to the summary, generate question and answer'})

text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to("cuda")

generated_ids = model.generate(**inputs, max_new_tokens=2048)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text3 = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print(output_text3[0])