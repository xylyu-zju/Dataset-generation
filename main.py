from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import json
import torch
import sys
from utils import prompt
from utils.prompt import (
    prompt_generate_summary_for_image1,
    prompt_generate_summary_for_image2,
    prompt_text_declare1,
    prompt_text_declare3,
    prompt_text_declare2,
)
import os
from docx import Document
from docx.shared import Inches
from PIL import Image
import io

# Add your dataset_extract path
sys.path.append('/home/xylv/python_code/dataset_extract')

# Define directories
root_directory = "/home/xylv/python_code/dataset_extract/resources/try"
results_dir = "/home/xylv/python_code/dataset_extract/results"
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
min_pixels = 256 * 28 * 28
max_pixels = 1280 * 28 * 28

def replace_repeated_dots(content):
    # Implement the function to replace repeated dots
    return content.replace('..', '.')

def process_docx(file_path):
    document = Document(file_path)
    structured_content = []
    current_heading = None
    current_level = 0

    def add_content_to_structure(heading, content, level):
        # Replace repeated dots and ensure the final content is formatted properly
        content = replace_repeated_dots(content).strip()
        structured_content.append({
            "level": level,
            "title": heading,
            "content": content
        })

    current_content = ''
    
    for para in document.paragraphs:
        # Detect headings
        if para.style.name.startswith('Heading') and int(para.style.name[-1]) <= 6:
            # Save the previous section if there was a previous heading
            if current_heading is not None:
                add_content_to_structure(current_heading, current_content, current_level)
            
            # Update current heading and level
            current_heading = para.text.strip()
            current_level = int(para.style.name[-1])  # Assumes heading levels are named 'Heading 1', 'Heading 2', etc.
            current_content = ''  # Reset content for the new section
        elif para.text.strip():  # If it's a non-empty paragraph, add to content
            current_content += para.text.strip() + "/n"
        else:
            current_content += '/n'  # Handle blank paragraphs as '/n'
    
    # Save the last section
    if current_heading is not None:
        add_content_to_structure(current_heading, current_content, current_level)
    
    return structured_content

def generate_summary_for_image(image, content):
    # Convert image to tensor
    processor = AutoProcessor.from_pretrained(model_dir,
                                              min_pixels=min_pixels,
                                              max_pixels=max_pixels
    )
    
    # First round: Generate summary based on the nearest heading level 6 or above
    nearest_heading = ""
    text_content = ""
    for item in reversed(content):
        if item['level'] <= 6:
            nearest_heading = item['title']
            text_content = item['content']
            break
    
    prompt_text = prompt_text_declare2.format(nearest_heading + "\n" + text_content)    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": os.path.join(image_directory, "temp_image.png"),  # 临时保存图片
                },
                {
                    "type": "text",
                    "text": nearest_heading + "\n" + text_content
                },
                {
                    "type": "text",
                    "text": prompt_text
                },
            ],
        }
    ]
    
    # Save the image temporarily
    image.save(os.path.join(image_directory, "temp_image.png"))
    
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
    if len(output_text) == 0:
        print("Warning: Generated text is empty!")
    else:
        print("First round output:", output_text[0])

    # Second round: Generate summary based on the first summary and image content
    messages.append({"role": "assistant", "content": output_text[0]})
    prompt_summary = prompt_generate_summary_for_image2.format(output_text[0])
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
    generated_ids = model.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    if len(output_text) is None:
        print("Warning: Generated text is empty!")
    else:
        print("Second round output:", output_text[0])

    return output_text[0]

def save_to_json(content, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    docx_path = os.path.join(root_directory, 'calbr_cmi_user.docx')
    json_path = os.path.join(results_dir, 'output.json')
    
    content = process_docx(docx_path)
    save_to_json(content, json_path)