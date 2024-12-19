prompt_generate_summary_for_image1 = """
You are now an AI assistant. Your task is to find the background and description corresponding to the picture in the text information based on the text information and pictures given to you, and then summarize the content of the picture and give a summary. If the picture contains text information, such as processes, tables, etc., please mainly describe the text content and its positional relationship. If the picture does not contain text, you need to focus on summarizing the use, purpose and information provided by the picture.The content you output should obey the following template:
```
<image description>
Here, you need to describe the content of the picture. If there is text content in the picture, please focus on describing the text content and their layout relationship. If the picture does not contain text, please describe the function, purpose and information conveyed by the picture.
```
Note:
1. If the picture contains text, describe its content and structure.
2. If the picture does not have text, focus on describing its information, use and intention.
3. The summary you make must be closely related to the picture.
4. The summary you make must be related to the part of the text content that corresponds to the picture.
5. If the provided picture and text information are not enough to generate <Summary>, directly output "no valuable summary can be drawn".
6. !!!Your answer must strictly follow the format of <image description> above!!!
7. Your answer should be as concise as possible!!! Do not generate repeated content!!!
Your answer is：
"""
prompt_generate_summary_for_image2 = """
You are now an AI assistant. Your task is to find the background and description of the image according to the text information given to you above, and then summarize the content of the image and give a summary. The content you output should follow the following template:
```
<image description>
Here you need to describe the summary of the image according to the text information and image content given to you, and give a summary.
```
Note:
1. If the image contains text, please describe its content and structure.
2. If there is no text in the image, please focus on describing its information, purpose and intention.
3. Your summary must be closely related to the image.
4. Your summary must be related to the text content corresponding to the image.
5. If the image and text information provided are not enough to generate <Summary>, directly output "No valuable summary can be drawn".
6. !!! Your answer must strictly follow the format of <image description> above!!!
7. Your answer should be as concise as possible!!! Do not generate repeated content!!!
Your answer is:
"""

prompt_text_declare1 = """"
You are now an AI assistant. All the above text content is text content related to the picture. Your task is to extract the information from this text that is related to the image. This extracted information will serve as a basis for summarizing the image. After analyzing the text, output the text description directly from this text that is related to the image.
```
<text description>
All the above content is text content related to the picture. Here, you need to get the information directly from this text that is related to the image.
```
Note:
1. The summary you make must be closely related to the image.
2. The summary you make must be related to the part of the text content that corresponds to the image.
3. If the provided image and text information are not enough to generate <Summary>, directly output "no valuable summary can be drawn".
4. Your answer must directly use the text description.
5. Your answer should be as concise as possible!!! Do not generate repeated content!!!
6. !!!Your answer must strictly follow the format of <text description> above!!!
Your answer is：
"""

prompt_text_declare2 = """"
All the above text contents are related to the picture. Your task is to find information related to the picture or information describing the picture from this text, and output the text description directly from this text related to the picture.
```
<Text description>
All the above text contents are related to the picture. Here you need to directly obtain the description of the picture content or information related to the picture from this text related to the picture. Please output the original text directly without summarizing.
```
Note:
1. The text you extract must be closely related to the picture.
2. If the picture and text information provided are not strongly related, please output "No information related to the picture was found in the text"
4. Your answer must be directly described in text.
5. Your answer should be as concise as possible! ! ! Do not generate repeated content! ! !
6. !!! Your answer must strictly follow the format of <Text description> above!!!
Your answer is:
"""
prompt_text_declare3 = """"
All the above text contents are related to the picture. Your task is to find information related to the picture or information describing the picture from this text, and output the text description directly from this text related to the picture.
```
<Text description>
All the above text contents are related to the picture. Here you need to directly obtain information that may be related to the picture from this text related to the picture, including but not limited to "figure", "flowing", "above" and other keywords that may describe the location of the picture. Please output the original text directly without summarizing.
```
Note:
1. The text you extract must be closely related to the picture.
2. Your answer must be directly described in text.
3. Your answer should be as concise as possible! ! ! Do not generate repeated content! ! !
4. !!! Your answer must strictly follow the format of <Text description> above!!!
Your answer is:
"""