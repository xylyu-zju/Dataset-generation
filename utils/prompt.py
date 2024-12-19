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
5. If the provided picture and text information are not enough to generate a Summary, directly output "no valuable summary can be drawn".
6. !!!Your answer must strictly follow the format of <image description> above!!!
7. Your answer should be as concise as possible! ! ! Do not generate repeated content! ! ! Do not generate meaningless content!!!
Your answer is：
"""
prompt_generate_summary_for_image2 = """
You are now an AI assistant. Your task is to find the background and description of the picture based on the text information given to you above, and then summarize the content of the picture and give a summary. The content you output should follow the following template:
```
<image description>
Here you need to give a summary of the picture content based on the text information given to you and the picture content.
```
Note:
1. If the picture contains text, please describe its content and structure.
2. If there is no text in the picture, please focus on describing its information, purpose and intention.
3. Your summary must be closely related to the picture.
4. Your summary must be related to the text content corresponding to the picture.
5. If the picture and text information provided are not enough to generate a summary, try to directly narrate the picture information.
6. !!! Your answer must strictly follow the format of <image description> above!!!
7. Your answer should be as concise as possible! !!!!!! Do not generate repeated content!!!!!!!!! ! Do not generate meaningless content!!!
Your answer is:
"""
prompt_generate_summary_for_image3 = """
You are now an AI assistant. Your task is to summarize the content of the image based on the text information given to you above.
```
<image description>
Here you need to give a summary of the image content based on the text information given to you and the image content.
```
Note:
1. If the image contains text, please describe its content and structure.
2. If there is no text in the image, please combine the text information given to you and focus on describing its information, purpose and intention.
3. Your summary must be closely related to the image.
4. Your summary should refer to the text information given to you.
5. !!! If the image and text information provided are not enough to generate a summary, please combine the image information and text to summarize!!!!!!
6. !!! Your answer must strictly follow the format of <image description> above!!!
7. Your answer should be as concise as possible
8. !!!!!! Do not generate repeated content!!!!!!!!! Do not generate meaningless content!!!
Your answer is:
"""
prompt_text_declare1 = """"
You are now an AI assistant. All the above text content is text content related to the picture. Your task is to extract the information from this text that is related to the image. This extracted information will serve as a basis for summarizing the image. After analyzing the text, output the text description directly from this text that is related to the image.
```
<text description>
Here, you need to get the information directly from this text that is related to the image. All the above content is text content related to the picture. 
```
Note:
1. The summary you make must be closely related to the image.
2. The summary you make must be related to the part of the text content that corresponds to the image.
3. If the provided image and text information are not enough to generate <Summary>, directly output "no valuable summary can be drawn".
4. Your answer must directly use the text description.
5. Your answer should be as concise as possible! ! !!!!!! Do not generate repeated content!!!!!!!!!! ! Do not generate meaningless content!!!
6. !!!Your answer must strictly follow the format of <text description> above!!!
Your answer is：
"""


prompt_text_declare2 = """"
You are an AI assistant. Your task is to find information related to the picture from the text given to you and summarize the information.
```
<Text description>
Here you need to find relevant content for the given image from the text and output a summary of the content for your picture. If you can't find relevant content, please output the last two sentences of text directly. Each sentence is divided by /n.
```
Note:
1. The text you extract must be closely related to the picture.
2. The summary you make must be related to the part of the text content that corresponds to the picture.
3. If the image and text information provided are not enough to generate <Text description>, directly output the last two sentences of text. Each sentence is divided by /n.
4. Your answer must be related to text.
5. Your answer should be as concise as possible! !!!!!!! Do not generate repeated content!!!!!!!!! ! ! Do not generate meaningless content!!!
6. ! ! ! Your answer must strictly follow the format of <Text description> above! ! ! !
Your answer is:
"""


prompt_text_declare3 = """"
You are an AI assistant. Your task is to find information related to the picture from the text given to you and summarize the information.
```
<Text description>
You need to find content related to the given picture from the text, and output a summary of the content of your picture and the last sentence in the text (divided by /n). If you cannot find relevant content, please output the last two sentences directly, each divided by /n.
```
Note:
1. The text you extract must be closely related to the picture.
2. The summary you make must be related to the part of the text corresponding to the picture.
3. If the picture and text information provided are not enough to generate <Text description>, directly output the last two sentences, each divided by /n.
4. Your answer must be related to the text.
5. Your answer should be as concise as possible! !!!!!!! Do not generate repeated content!!!!!!!!! ! ! Do not generate meaningless content! ! !
6. ! ! ! Your answer must strictly follow the format of <Text description> above! ! ! !
Your answer is:
"""

prompt_datasetgeneration = """"
You are an AI assistant, and your task is to generate answers based on picture and questions.
```
<Text description>
You need to generate answers for each of the above questions based on the image. The image shows a defect in an SEM image: a hole.
```
Note:
The answer must be closely related to the question.
Your response must be relevant to the image.
Keep your response as concise as possible!!!!!!! Do not generate repetitive content!!!!!!! Do not generate meaningless content!!!!!!!
!!! Your response must strictly follow the format of the above <Text description>!...
Output the answers in the order of the questions, with each answer on a new line!!!
Your answer is:
"""

prompt_class_questions_cause = """"
Please generate 10 diverse questions about the causes or reasons behind a defect. This image has a hole as defect in SEM image. There are some examples in <question template>:
<question template>
'How was this defect caused?',
'What factors led to the occurrence of this defect?',
'What caused this defect to arise?',
'What is responsible for the existence of this problem?',
'What factors contributed to the occurrence of this defect?',
'What are the reasons behind the occurrence of this defect?',
'What led to the generation of this defect?',
'What is the fundamental reason behind this issue?',
'Which factors triggered the emergence of this defect?',
'Why did this defect occur?'.
Note:
1.The questions should be similar in style to the examples below but not limited to them.
2.The questions should explore what caused the defect, the factors that contributed to its occurrence, or the fundamental reasons behind it. 
3.Ensure the questions are varied in phrasing, avoiding repetition, while maintaining clear and appropriate meaning for different contexts. 
4. Your answer should be as concise as possible! !!!!!!! Do not generate repeated content!!!!!!!!! ! ! Do not generate meaningless content! ! !
"""

prompt_class_questions_cause_solve= """"
Please generate a diverse set of questions about the way to solve the defect. There are some examples in <question template>:
<question template>
'How can we address these deficiencies?',
'How to avoid these defects?',
'How can we avoid the occurrence of these defects in the production process?',
'What are the methods for resolving these shortcomings?',
'What measures should we take to overcome these deficiencies?',
'Are there viable solutions for these shortcomings?',
'What steps should be taken to rectify these deficiencies?',
'How can we effectively fix these flaws?',
'Are there practical solutions for addressing these shortcomings?',
'What measures can we adopt to compensate for the existence of these deficiencies?',
'What strategies can be employed to tackle these deficiencies?',
'What methods are available for resolving these shortcomings?',
'How to address these deficiencies?'
Note:
1.The questions should be similar in style to the examples below but not limited to them.
2.The questions should explore what caused the defect, the factors that contributed to its occurrence, or the fundamental reasons behind it. 
3.Ensure the questions are varied in phrasing, avoiding repetition, while maintaining clear and appropriate meaning for different contexts. 
4. Your answer should be as concise as possible! !!!!!!! Do not generate repeated content!!!!!!!!! ! ! Do not generate meaningless content! ! !
"""

prompt_class_questions_what = """"
"""

class_questions = """"
"""