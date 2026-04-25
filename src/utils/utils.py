
import yaml
import json
import os
from box import Box
from src.utils.emotion_detector import EmotionDetector
import re
import tiktoken

MAX_INPUT_TOKEN_NUM = 128000

def load_config(config_path):
    config = Box.from_yaml(
        filename=config_path, Loader=yaml.FullLoader)
    return config


def emotion_detection(content, intensity_threshold=0.2):
    ed = EmotionDetector()
    emotions = ed.get_text_emo(content)
    cleaned_emotions = []
    if len(emotions) != 0:
        for e in emotions:
            intensity = float(ed.get_emo_intensity(content, e))
            if intensity >= intensity_threshold:
                cleaned_emotions.append((e, intensity))
    cleaned_emotions.sort(key=lambda x: x[1], reverse=True)
    return cleaned_emotions



def save_as_json(path, data):
    '''
    outout a json file with indent equals to 2
    '''
    json_data = json.dumps(data, indent=2)
    # Save JSON to a file
    try:
        # Create the directory structure if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Write data to the JSON file
        with open(path, 'w') as json_file:
            json_file.write(json_data)

        print(f"Experiment results written to '{path}' successfully.")

        class ContextAttributeError(BaseException):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)

        return True
    except Exception as e:
        print(f"Failed to write experiment results to '{path}': {e}")
        return False

    pass

def process_autobiography(file_path):
    '''
    load plain text file and divide into chapters for incremental summarization.
    default chapter format: r'CHAPTER \d+'
    chapters will be save as json file
    '''

    with open(file_path, 'r') as f:
        text = f.read()

    # match the position of beginning and ending of CHAPTER x identifier
    chapter_positions = [match.start() for match in re.finditer(r'CHAPTER \d+', text)]
    chapter_positions.append(len(text))  # 添加文本的结束位置

    # save chapter name: chapter context in json
    chapters = {}
    for i in range(len(chapter_positions) - 1):
        start = chapter_positions[i]
        end = chapter_positions[i + 1]
        chapter_name = text[start:text.index('\n', start)]
        chapter_content = text[text.index('\n', start) + 1:end].strip()
        chapters[chapter_name] = chapter_content

    # output json file
    with open(file_path+'.json', 'w') as f:
        json.dump(chapters, f)

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def check_truncate_prompt(prompt, string, encoding_name: str = "cl100k_base"):
    '''
    count token num of prompt template+string
    truncate string if exceed max input token num 
    '''
    token_num = num_tokens_from_string(prompt) 
    if token_num > MAX_INPUT_TOKEN_NUM:
        tokenzier = tiktoken.get_encoding(encoding_name)
        truncate_amount = MAX_INPUT_TOKEN_NUM-token_num
        encoded = tokenzier.encode(string)
        new_string = tokenzier.decode(encoded[truncate_amount:])
        return new_string
    else:
        return None