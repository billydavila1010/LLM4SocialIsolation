from src.eval.eval_prompts import construct_event_summarization_prompt
import json, os, re
from src.agents.chat_llm import chat_llm
from src.utils.utils import load_config
from typing import Dict
import argparse

def _load_autobiography(autobiography_path):
    """
    load autobiography summarization
    :param autobiography_path: path to autobiography
    :return:
    """
    if not os.path.exists(autobiography_path):
        raise FileNotFoundError
    if autobiography_path.endswith('.json'):
        with open(autobiography_path, 'rb') as f:
            autobiography = json.load(f)
    else:
        with open(autobiography_path) as f:
            autobiography = f.read()
    return autobiography


def _extract_event_from_autobiography(autobiography: Dict|str, agent_config, save_to_local=False):
    '''
    Apply prompt template and input LLM to extract events from autobiography
    '''
    msg = {}
    msg['role'] = "user"
    if isinstance(autobiography, dict):
        events = {}
        for chapter, content in autobiography.items():
            print(f'Extract events {chapter}')
            msg['content'] = construct_event_summarization_prompt(content)
                
            event_extract_response = chat_llm(
                messages=[msg],
                model=agent_config.llm_model_path,
                temperature=agent_config.temperature,
                max_tokens=agent_config.max_tokens,  # currently fixed, can be added to config
                n=1,
                timeout=agent_config.timeout,
                stop=None
            )
            events[chapter] = event_extract_response['generations'][0]
            print(f'{chapter} summary is: \n {events.items()}')
    else:
        msg['content'] = construct_event_summarization_prompt(autobiography)
        event_extract_response = chat_llm(
            messages=[msg],
            model=agent_config.llm_model_path,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            n=1,
            timeout=agent_config.timeout,
            stop=None
        )

        events = event_extract_response['generations'][0]

    if save_to_local:
        print(f'Save events to {agent_config.autobiography_pre_event_path}')
        with open(agent_config.autobiography_pre_event_path, 'w') as f:
            json.dump({'event': events}, f)

    return events

def execute_extraction(agent_config_path, save_to_local=False):
    '''
    load LLM config and autobio for event extraction 
    output format:
    {"event": {"CHAPTER 1": "extraction"}, {"CHAPTER 2": "extraction"}, ...}}
    '''
    agent_config = load_config(agent_config_path)
    autobio_path = agent_config.autobiography_path_for_summary
    autobio = _load_autobiography(autobio_path)
    events = _extract_event_from_autobiography(autobio, agent_config, save_to_local)
    return events


def post_processing(agent_config_path):
    """
    parse event extraction output
    output format:
    {"CHAPTER 1": [["time", "summary"], ["time", "summary"], ...], 
    "CHAPTER 2": [["time", "summary"], ..], ...}
    """
    agent_config = load_config(agent_config_path)
    output_path = agent_config.autobiography_pre_event_path
    parsed_output_path= getattr(agent_config, 'autobiography_event_parsed_path', None)

    with open(output_path) as f:
        ch2events = json.load(f)
    
    ch2parsed_events = {} 
    
    for ch, items in ch2events['event'].items():
        items += '\n'
        pattern = r"Event Time: (.*?)\n+Summary: (.*?)\n+"
        matches = re.findall(pattern, items, re.DOTALL)

        ch2parsed_events[ch] = [(time.strip(), summary.strip()) for time, summary in matches]
    
    if not parsed_output_path:
        parsed_output_path = output_path.replace('.json', '_parsed.json')
    
    print(f'Save parsed events to {parsed_output_path}')
    with open(parsed_output_path, 'w') as f:
        json.dump(ch2parsed_events, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval-config-path', type=str, default='./src/configs/patient_config.yaml')
    parser.add_argument('--save-to-local', action='store_true')
    parser.add_argument('--openai-api-key', type=str, default='sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE')
    parser.add_argument('--parse-result', type=str, default=None)
    args = parser.parse_args()

    os.environ["OPENAI_API_KEY"] = args.openai_api_key
    agent_config_path = args.eval_config_path
    events = execute_extraction(agent_config_path, save_to_local=args.save_to_local)
    for k,v in events.items():
        print(v)
    
    if args.save_to_local and args.parse_result:
        post_processing(agent_config_path)