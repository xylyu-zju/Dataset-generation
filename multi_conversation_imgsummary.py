from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import json
import torch
import sys
from utils import prompt
from utils.prompt import (
    prompt_generate_summary_for_image1,
    prompt_generate_summary_for_image2,
    prompt_generate_summary_for_image3,
    prompt_text_declare1,
    prompt_text_declare3,
    prompt_text_declare2,
)
import os
from docx import Document
from docx.shared import Inches
from PIL import Image
import io
import time
import re

# Add your dataset_extract path
sys.path.append('/home/xylv/python_code/dataset_extract')

# Define directories
root_directory = "/home/xylv/dataset/word"
results_dir = "/home/xylv/python_code/dataset_extract/results/json"
model_dir = "/home/xylv/.cache/modelscope/hub/qwen/Qwen2-VL-2B-Instruct"
image_directory = "/home/xylv/python_code/dataset_extract/resources/images"

# Ensure the image directory exists
os.makedirs(image_directory, exist_ok=True)

# Load the model with recommended settings
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_dir,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

# Initialize the processor with appropriate pixel ranges
min_pixels = 128 * 28 * 28

def process_docx(file_path):
    start_time = time.time()
    document = Document(file_path)
    content = []
    current_heading = None
    current_content = ""
    for para in document.paragraphs:
        if para.style.name.startswith('Heading') and not para.style.name.endswith('7'):
            if current_heading:
                # Save the previous heading and its content
                current_heading['content'] = re.sub(r'\n{2,}', '\\n', current_content)
                content.append(current_heading)
            level = int(para.style.name[-1])
            current_heading = {'type': 'heading', 'level': level, 'text': para.text}
            current_content = ""
        elif para.runs and para.runs[0].element.xpath('.//pic:pic'):
            for run in para.runs:
                for pic in run.element.xpath('.//pic:pic'):
                    image = pic.blipFill.blip.embed
                    image_stream = document.part.related_parts[image].blob
                    image = Image.open(io.BytesIO(image_stream))
                    if image is not None:
                        # Check image size
                        width, height = image.size
                        if min_pixels <= width * height:
                            # Check and adjust aspect ratio
                            aspect_ratio = width / height
                            if abs(aspect_ratio) > 200:
                                print(f"Image aspect ratio {aspect_ratio} not within range, skipping.")
                                continue
                            print(f"Processing image with size: {width}x{height}")
                            summary = generate_summary_for_image(image, current_heading, re.sub(r'\n{2,}', '\\n', current_content))
                            image_info = {'type': 'image', 'content': summary}
                            content.append(image_info)
                        else:
                            print(f"Image size {width * height} not within range, skipping.")
                    else:
                        print("Warning: Image is None")
        else:
            current_content += para.text + "\n"
    if current_heading:
        # Save the last heading and its content
        current_heading['content'] = re.sub(r'\n{2,}', '\\n', current_content)
        content.append(current_heading)
    return content

def generate_summary_for_image(image, heading, content):
    start_time = time.time()
    messages=[]
    processor = AutoProcessor.from_pretrained(model_dir, min_pixels=min_pixels)
    text_content = heading['text'] + "\n" + content if heading else content
    prompt_text = prompt_text_declare3.format(text_content)    
    message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": os.path.join(image_directory, "temp_image.png"),  # 临时保存图片
                },
                {
                    "type": "text",
                    "text": text_content
                },
                {
                    "type": "text",
                    "text": prompt_text
                },
            ],
        }
    image.save(os.path.join(image_directory, "temp_image.png"))
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
    generated_ids = model.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    if len(output_text) == 0:
        print("Warning: Generated text is empty!")
    else:
        print("First round output:", output_text[0])

    # Second round: Generate summary based on the first summary and image content
    messages.append({"role": "assistant", "content": output_text[0]})
    prompt_summary = prompt_generate_summary_for_image3.format(output_text[0])
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": os.path.join(image_directory, "temp_image.png"),
                },
                {
                    "type": "text",
                    "text": prompt_summary
                },
            ],
        }
    )

    # Preparation for second inference
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
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text1 = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    if len(output_text1) == 0:
        print("Warning: Generated text is empty!")
    else:
        print("Second round output:", output_text1[0])
        #error rate
    if "Here you need to" in output_text1[0] or "Here you need to" in output_text[0]:
        print("Detected 'Here you need to', regenerating summary...")
        return generate_summary_for_image(image, heading, content)

    # 检测输出结果是否少于20个字母
    if len(output_text1[0]) < 20:
        print("Output text is less than 20 characters, regenerating summary...")
        return generate_summary_for_image1(image, heading, content)

    return output_text1[0]

def generate_summary_for_image1(image, heading, content):
    start_time = time.time()
    messages=[]
    processor = AutoProcessor.from_pretrained(model_dir, min_pixels=min_pixels)
    text_content = heading['text'] + "\n" + content if heading else content
    prompt_text = prompt_generate_summary_for_image3.format(text_content)    
    message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": os.path.join(image_directory, "temp_image.png"),  # 临时保存图片
                },
                {
                    "type": "text",
                    "text": text_content
                },
                {
                    "type": "text",
                    "text": "describe the image according to the text"
                },
            ],
        }
    image.save(os.path.join(image_directory, "temp_image.png"))
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
    generated_ids = model.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    if len(output_text) == 0:
        print("Warning: Generated text is empty!")
    else:
        print("First round output:", output_text[0])
    if "Here you need to" in output_text[0] or "Here you need to" in output_text[0]:
        print("Detected 'Here you need to', regenerating summary...")
        return generate_summary_for_image1(image, heading, content)
    else:
        return output_text[0]
    
def save_to_json(content, output_path):
    start_time = time.time()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
    print(f"JSON saving time: {time.time() - start_time} seconds")

if __name__ == "__main__":
    for filename in os.listdir(root_directory):
        if filename.endswith(".docx"):
            docx_path = os.path.join(root_directory, filename)
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(results_dir, json_filename)
            
            print(f"Processing document: {docx_path}")
            content = process_docx(docx_path)
            print(f"Saving results to: {json_path}")
            save_to_json(content, json_path)
            print(f"Processing complete for {filename}.")