from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from modelscope import snapshot_download
import torch
import os
import time
import textwrap
import matplotlib.pyplot as plt
# model_dir = snapshot_download("qwen/Qwen2-VL-7B-Instruct")
model_dir = "/home/xlzhou/.cache/modelscope/hub/qwen/Qwen2-VL-7B-Instruct"
png_dir = "/home/xlzhou/pngs"
summary_dir = "/home/xlzhou/qwen/summary_test"
words = 50
en_prompt = f"Shortly summary these images within {words} words."
ch_prompt = f"简要概括这些图像，{words}字以内"
# default: Load the model on the available device(s)
'''
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_dir, torch_dtype="auto", device_map="auto"
)
'''
# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
# print(model_dir)
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_dir,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

# default processer
processor = AutoProcessor.from_pretrained(model_dir)

# The default range for the number of visual tokens per image in the model is 4-16384. You can set min_pixels and max_pixels according to your needs, such as a token count range of 256-1280, to balance speed and memory usage.
# min_pixels = 256*28*28
# max_pixels = 1280*28*28
# processor = AutoProcessor.from_pretrained(model_dir, min_pixels=min_pixels, max_pixels=max_pixels)

def content_generate(images):
    '''
    Give a set of images and generate a summary
    '''
    content_list = []
    # Preparation for inference
    for img in images:
        content_list.append({ "type": "image", "image": img })
    content_list.append({ "type": "text", "text": ch_prompt })
    messages = [
        {"role": "system", "content": "you are an expert in the field of intergrated circurt manufacturing."},
        {"role": "user", "content": content_list}
    ]
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
    generated_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    return (output_text)

summary = []
exe_time = []
for folder in os.listdir(png_dir):
    img_dir = os.path.join(png_dir, folder)
    if os.path.isdir(img_dir) and img_dir == "/home/xlzhou/pngs/55nm  process--1":
        batch_size = 4
        imgs = os.listdir(img_dir)
        for _ in range(0, len(imgs), batch_size):
            batch = imgs[_ : _ + batch_size]
            batch_path = [os.path.join(img_dir, name) for name in batch]
            start_time = time.time()
            content = content_generate(batch_path)
            end_time = time.time()
            exe_time.append(round(end_time - start_time, 3))
            summary.append(content[0])
#           print(content[0] + f"\n exe_time : {exe_time}\n")

output = os.path.join(summary_dir,"output.txt")
with open(output, "w") as file:
    for _ , t in zip(summary, exe_time):
        wrapped_text = textwrap.wrap(_, width=100)
        for line in wrapped_text:
            file.write(line+"\n")
        file.write(f"\n exe_time : {t:.3f}\n\n")
x_axis = list(range(1, len(exe_time)+1))
plt.plot(x_axis, exe_time)
plt.title('Inference time')
plt.ylabel('time/s')
plt.savefig(summary_dir+'/plot.png')
plt.show()