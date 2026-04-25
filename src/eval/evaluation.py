import numpy as np
import os
import tqdm
import re
import sys
from src.utils.utils import load_config
import json
import argparse
from src.eval.conversation_eval_prompt import fluecny_prompt, identify_prompt, comfort_prompt, question_quality, fluency_gpt4judge_prompt
from src.eval.gpt4_judge_prompt import fluency_judge, comfort_judge, question_judge, insightfulness_judge, narrativity_judge, emotional_judge
from src.agents.chat_llm import chat_llm
from src.eval.eval_prompts import construct_gpt_eval_prompt_simplified
from src.memory.memory_graph import TimeIndexedMemoryGraph, MemoryNode


def extract_events_from_conv(conv_folder, graph_config):
    graph = TimeIndexedMemoryGraph(graph_config)
    events = []
    if 'extracted_events.json' in os.listdir(conv_folder):
        with open(os.path.join(conv_folder, 'extracted_events.json')) as f:
            return json.load(f)

    for conv in tqdm.tqdm(os.listdir(conv_folder)):
        if conv != 'extracted_events.json' and conv != 'extracted_events_session_splits.json':
            conf_f = os.path.join(conv_folder, conv)
            with open(conf_f, 'r') as f:
                conversation = json.load(f)['conversation']
                conv_str = ''
                for c in conversation:
                    role = c[0]
                    content = c[1].replace('\n', ' ')
                    conv_str += f'{role}: {content}\n'
            events.append(graph.extract_events(conv_str))

    with open(os.path.join(conv_folder, 'extracted_events.json'), 'w') as f:
        mem_nodes = []
        for n in events:
            mem_nodes += [_.to_json() for _ in n]
        json.dump(mem_nodes, f)

    with open(os.path.join(conv_folder, 'extracted_events_session_splits.json'), 'w') as f:
        json.dump([[n.to_json() for n in node] for node in events], f)
    return mem_nodes


def interviewing_coverage_date(gt_events, extracted_events):
    gt_dates = [e[0] for e in gt_events]
    extracted_dates = [e['date'] if not isinstance(e, MemoryNode) else e.date for e in extracted_events]

    def _preprocess_date(date_list):
        new_date = []
        for d in date_list:
            search = re.search('(\d{4})', d)
            if search:
                _new_date = int(search.group(1))
                new_date.append(round(_new_date / 5) * 5)
        new_date = sorted(new_date)
        return list(set(new_date))

    print(gt_dates)
    print(extracted_dates)
    gt_dates = _preprocess_date(gt_dates)
    extracted_dates = _preprocess_date(extracted_dates)
    intersection = set(gt_dates).intersection(set(extracted_dates))
    print(len(intersection) / len(gt_dates))
    return len(intersection) / len(gt_dates)


def interviewing_coverage_chapter(autobiography_path, conv_history_folder):
    with open(autobiography_path) as f:
        chapters = json.load(f)

    retrieved_chapters = []
    for f in os.listdir(conv_history_folder):
        retrieved_chapters += _interviewing_coverage_chapter(chapters, os.path.join(conv_history_folder, f))
    retrieved_chapters = list(set(retrieved_chapters))
    print(len(retrieved_chapters))


def get_user_responses(conv_fp):
    with open(conv_fp) as f:
        conv = json.load(f)['conversation']

    user_responses = []
    for c in conv:
        if c[0] == 'patient':
            user_responses.append(c[1])
    return '\n'.join(user_responses)

def get_conversation(conv_fp):
    with open(conv_fp) as f:
        conv = json.load(f)['conversation']
    conv_str = ''
    for c in conv:
        if c[0] == 'doctor':
            role = c[0]
            content = c[1].replace('\n', ' ')
            conv_str += f'Interviewer: {content}\n'
        elif c[1] == 'patient':
            role = c[0]
            content = c[1].replace('\n', ' ')
            conv_str += f'User: {content}\n'
    return conv_str


def get_retrieved_documents(conv_fp):
    if conv_fp.endswith('.json'):
        with open(conv_fp) as f:
            conv = json.load(f)

        retrieved = []

        for d in conv['patient']['patient_context']:
            content = d['content']
            match = re.search(r'======= Document Begin =========\n(.*?)======= Document End =========', content,
                              re.DOTALL)
            if match:
                if not match.group(1) in retrieved:
                    retrieved.append(match.group(1))
    elif conv_fp.endswith('.txt'):
        retrieved = []
        with open(conv_fp) as f:
            lines = f.readlines()
            for l in lines:
                if l.startswith('Run '):
                    new_run = 0

                if l.startswith('RETRIEVE document: ') and new_run < 10:
                    document = l.replace('RETRIEVE document: ', '')
                    if document not in retrieved:
                        retrieved.append(document)
                    new_run += 1
    else:
        raise NotImplementedError
    return retrieved


def _interviewing_coverage_chapter(chapters, conv_fp):
    retrieved = get_retrieved_documents(conv_fp)

    retrieved_chapters = []
    for i in retrieved:
        found = False
        for k, v in chapters.items():
            i_no_space = re.sub(r'\s', '', i)
            v_no_space = re.sub(r'\s', '', v)
            if i_no_space in v_no_space:
                print(f'in {k}')
                # print(i_no_space)
                # print(v_no_space)
                found = True
                if k not in retrieved_chapters:
                    retrieved_chapters.append(k)
        if not found:
            print(i)
            print('Retrieved Failed')

    return retrieved_chapters


def load_groundtruth_events(gt_events):
    '''
    load all ground truth events into a string as one document
    '''
    with open(gt_events) as f:
        df = json.load(f)
    times = []
    events = []
    for ch, items in df.items():
        import pdb
        # pdb.set_trace()
        for item in items:
            times.append(item[0])
            events.append(item[1])

    full_text = ''
    for x, y in zip(times, events):
        full_text += f'In {x}, {y}\n'

    return full_text


def load_gt_events(path):
    gt_events = []
    with open(path) as f:
        events = json.load(f)
        for k, v in events.items():
            for e in v:
                gt_events.append(e)
    return gt_events


def extract_content(tag, text):
    # Find the starting position of the tag
    start_idx = text.find(tag)

    # If tag is not found, return None
    if start_idx == -1:
        if text.isdigit():
            return int(text)
        else:
            return None

    # Extract the content after the tag
    content_after_tag = text[start_idx + len(tag):].strip()

    # Split the content by whitespace
    parts = content_after_tag.split()

    # If the first part (immediately after the tag) is a number, return it, else return the entire content after the tag
    if tag == "#thescore: ":
        assert parts[0].isdigit()
        return int(parts[0])
    else:
        end_idx = text.find("#", start_idx + 1)
        return content_after_tag if end_idx == -1 else content_after_tag[:end_idx].strip()

def conversation_eval(conversation, metric):
    if metric == 'fluency':
        prompt = fluecny_prompt.format(conversation=conversation)
    elif metric == 'identity':
        prompt = identify_prompt.format(conversation=conversation)
    elif metric == 'comfort':
        prompt = comfort_prompt.format(conversation=conversation)
    elif metric == 'question_quality':
        prompt = question_quality.format(conversation=conversation)
    elif metric == 'quality_gpt4judge':
        prompt = fluency_gpt4judge_prompt.format(conversation=conversation)
    else:
        raise NotImplementedError
    return _query(prompt)['generations'][0]

def conversation_compare(conv1, conv2, metric):
    if metric == 'fluency':
        prompt = fluency_judge.format(conv1=conv1, conv2=conv2)
    elif metric == 'comfort':
        prompt = comfort_judge.format(conv1=conv1, conv2=conv2)
    elif metric == 'question':
        prompt = question_judge.format(conv1=conv1, conv2=conv2)
    else:
        raise NotImplementedError

    return _query(prompt)['generations'][0]

def autobio_compare(conv1, conv2, metric):
    if metric == 'insightfulness':
        prompt = insightfulness_judge.format(conv1=conv1, conv2=conv2)
    elif metric == 'narrativity':
        prompt = narrativity_judge.format(conv1=conv1, conv2=conv2)
    elif metric == 'emotional':
        prompt = emotional_judge.format(conv1=conv1, conv2=conv2)
    else:
        raise NotImplementedError

    return _query(prompt)['generations'][0]


def _query(prompt):
    msgs = []
    msg = {}
    msg['role'] = "user"
    msg['content'] = prompt
    msgs.append(msg)

    response = chat_llm(
        messages=msgs,
        model='gpt-4o',
        temperature=0,
        max_tokens=1024,
        n=1,
        timeout=600,
        stop=None
    )
    return response

def load_autobiography(autobio_path):
    with open(autobio_path) as f:
        autobio = json.load(f)
    selected_p = []
    for _autobio in autobio:
        # paras = _autobio.split('\n')
        # selected_p.append('\n'.join(paras[(len(paras) // 2) -2 : (len(paras) // 2) + 2]))
        selected_p.append(_autobio)
    return selected_p

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval-config-path', type=str, default='./src/configs/obama_config.yaml')
    # parser.add_argument('--eval-config-path', type=str, default='./src/configs/jane_eyre_config.yaml')
    # parser.add_argument('--eval-config-path', type=str, default='./src/configs/catherine_helen_spence.yaml')
    # parser.add_argument('--eval-config-path', type=str, default='./src/configs/anthony_trollope.yaml')

    # parser.add_argument('--conv-history-folder', type=str, default='./experiments/conv_history_w_interview_protocol_w_memorygraph_w_emotion_gpt4o/Obama/conv')
    parser.add_argument('--memory-graph-folder', type=str, default=None)
    # parser.add_argument('--memory-graph-folder', type=str, default='./experiments/conv_history_w_interview_protocol_w_memorygraph_w_emotion_gpt4o/Obama/memory_graph')

    parser.add_argument('--conv-history-folder', type=str, default='./experiments/Catherine_Helen_Spence/Catherine_Helen_Spence_conv')
    # parser.add_argument('--memory-graph-folder', type=str, default='./experiments/Catherine_Helen_Spence/Catherine_Helen_Spence_memory_graph')

    # parser.add_argument('--conv-history-folder', type=str, default='./experiments/Anthony_Trollope/conv')
    # parser.add_argument('--memory-graph-folder', type=str, default='./experiments/Anthony_Trollope/memory_graph')

    # parser.add_argument('--conv-history-folder', type=str, default='./experiments/Jane_Eyre/Jane_Eyre_conv')
    # parser.add_argument('--memory-graph-folder', type=str, default='./experiments/Jane_Eyre/Jane_Eyre_memory_graph')

    parser.add_argument('--autobio-folder', type=str, default='./autobiography_generation/guidellm/Catherine_Helen_Spence/autobiography.json')


    # parser.add_argument('--memory-graph-folder', type=str, default=None)
    # parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/anthony_trollope/gpt-4o')
    # parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/anthony_trollope/gpt-4-turbo')
    # parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/anthony_trollope/mixtral')
    # parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/anthony_trollope/qwen2-72b')
    # parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/anthony_trollope/llama3-8b')
    # parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/anthony_trollope/llama3-70b')

    parser.add_argument('--eval-result-path', type=str, default='./eval_results.json')
    parser.add_argument('--graph-config', type=str, default='./src/configs/memory_graph_config.yaml')
    parser.add_argument('--extracted-events', type=str, default='')
    parser.add_argument('--metric', type=str, default='coverage-date', choices=['coverage-chapter', 'coverage-date', 'correctness', 'conversation', 'conversation-compare', 'autobiography'])

    os.environ['OPENAI_API_KEY'] = 'sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE'

    args = parser.parse_args()
    config = load_config(args.eval_config_path)

    gt_events = load_gt_events(config.autobiography_pre_event_path)

    result = None
    if args.metric == 'coverage-chapter':
        # result = interviewing_coverage_chapter(config.autobiography_path_for_summary, args.conv_history_folder)
        print(interviewing_coverage_chapter(config.autobiography_path_for_summary, args.conv_history_folder))
    elif args.metric == 'coverage-date':
        if args.memory_graph_folder is None:
            events = extract_events_from_conv(args.conv_history_folder, args.graph_config)
        else:
            graph_file = sorted(os.listdir(args.memory_graph_folder))[-1]
            graph = TimeIndexedMemoryGraph(args.graph_config)
            graph.load(os.path.join(args.memory_graph_folder, graph_file))
            events = graph.time_indexed_memory_chain
        print(events)
        # result = interviewing_coverage_date(gt_events, events)
        print(interviewing_coverage_date(gt_events, events))
    elif args.metric == 'correctness':
        # load events per session
        if args.memory_graph_folder is None:
            with open(os.path.join(args.conv_history_folder, 'extracted_events_session_splits.json')) as f:
                events_per_session = json.load(f)
        else:
            memory_files = sorted(os.listdir(args.memory_graph_folder))
            events_per_session = []

            last_idx = -1
            for mem_idx, mem_f in enumerate(memory_files):
                current_mem = os.path.join(args.memory_graph_folder, mem_f)
                with open(current_mem) as f:
                    current_mem = json.load(f)['time_indexed_memory_chain']
                if mem_idx >= 1:
                    last_mem = os.path.join(args.memory_graph_folder, memory_files[mem_idx - 1])
                    with open(last_mem) as f:
                        last_mem = json.load(f)['time_indexed_memory_chain']
                else:
                    last_mem = []

                session_events = current_mem[len(last_mem):]
                events_per_session.append(session_events)

        conv_files = sorted([_ for _ in os.listdir(args.conv_history_folder) if not _.startswith('extracted')])

        assert len(conv_files) == len(events_per_session)
        eval_results = []
        len_gt_events = len(gt_events)
        for conv_f, events in tqdm.tqdm(zip(conv_files, events_per_session)):
            user_responses = get_user_responses(os.path.join(args.conv_history_folder, conv_f))
            for event in events:
                event_date = event['date']
                event_people = event['people_involved']
                event_topic = event['topic']
                event_description = event['description']
                event_descrip = f'Date: {event_date} People: {event_people} Topic: {event_topic} Description: {event_description}'
                prompt = construct_gpt_eval_prompt_simplified(event_descrip, user_responses)
                response = _query(prompt)
                score = extract_content('#thescore: ', response['generations'][0])
                eval_results.append(score)

        precision = np.mean(eval_results)
        recall = np.sum(eval_results) / len(gt_events)
        f1 = 1 * (precision * recall) / (precision + recall)
        result = {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        print(f'Precision: {precision}\tRecall: {recall}\tF1: {f1}')
    elif args.metric == 'conversation-score':
        # evaluate the quality of conversation
        # generate conversation
        conv_files = sorted([_ for _ in os.listdir(args.conv_history_folder) if not _.startswith('extracted')])
        eval_results = []
        len_gt_events = len(gt_events)
        fluency_score_list = []
        identity_score_list = []
        comfort_score_list = []
        for conv_f in tqdm.tqdm(conv_files):
            session_conversation = get_conversation(os.path.join(args.conv_history_folder, conv_f))
            print(session_conversation)
            print('\n\n\n')
            fluency_response = conversation_eval(session_conversation, metric='fluency')
            identity_response = conversation_eval(session_conversation, metric='identity')
            comfort_response = conversation_eval(session_conversation, metric='comfort')
            fluency_score = extract_content('#thescore: ', fluency_response)
            identity_score = extract_content('#thescore: ', identity_response)
            comfort_score = extract_content('#thescore: ', comfort_response)
            print(fluency_score, fluency_response)
            print(identity_response)
            print(comfort_response)
            print(f'Identity: {identity_score}')
            print(f'Fluency: {fluency_score}\tIdentity: {identity_score}\tComfort: {comfort_score}')
            fluency_score_list.append(fluency_score)
            identity_score_list.append(identity_score)
            comfort_score_list.append(comfort_score)
        print(f'Averaged: Fluency: {np.mean(fluency_score_list)}\tIdentity: {np.mean(identity_score_list)}\tComfort: {np.mean(comfort_score_list)}')
        print(f'Averaged: Identity: {np.mean(identity_score_list)}')
    elif args.metric == 'conversation-compare':
        opponent_conv_root = './baseline_exp/Jane_Eyre'
        opponent_llm_list = ['gpt-4-turbo', 'gpt-4o', 'llama3-8b', 'llama3-70b', 'mixtral', 'qwen2-72b']
        # opponent_llm_list = ['llama3-8b', 'llama3-70b', 'mixtral', 'qwen2-72b']
        result = {}
        for opponent_llm in tqdm.tqdm(opponent_llm_list):
            opponent_conv_folder = os.path.join(opponent_conv_root, opponent_llm)

            conv_files = sorted([_ for _ in os.listdir(args.conv_history_folder) if not _.startswith('extracted')])
            opponent_conv_files = sorted([_ for _ in os.listdir(opponent_conv_folder) if not _.startswith('extracted')])
            conversations = [get_conversation(os.path.join(args.conv_history_folder, f)) for f in conv_files]
            opponent_conversations = [get_conversation(os.path.join(opponent_conv_folder, f)) for f in opponent_conv_files]
            opponent_conversations = opponent_conversations * 10
            np.random.shuffle(opponent_conversations)
            fluency_WR = 0
            fluency_LR = 0
            question_WR = 0
            question_LR = 0
            comfort_WR = 0
            comfort_LR = 0

            result[opponent_llm] = {}

            for conv, opp_conv in tqdm.tqdm(zip(conversations, opponent_conversations[:len(conversations)])):
                fluency_resp = conversation_compare(conv, opp_conv, metric='fluency')
                question_resp = conversation_compare(conv, opp_conv, metric='question')
                comfort_resp = conversation_compare(conv, opp_conv, metric='comfort')
                if '[[A]]' in fluency_resp:
                    fluency_WR += 1
                elif '[[B]]' in fluency_resp:
                    fluency_LR += 1

                if '[[A]]' in question_resp:
                    question_WR += 1
                elif '[[B]]' in question_resp:
                    question_LR += 1

                if '[[A]]' in comfort_resp:
                    comfort_WR += 1
                elif '[[B]]' in comfort_resp:
                    comfort_LR += 1

                result[opponent_llm] = {
                    'fluency_WR': fluency_WR / len(conversations),
                    'fluency_LR': fluency_LR / len(conversations),
                    'question_WR': question_WR / len(conversations),
                    'question_LR': question_LR / len(conversations),
                    'comfort_WR': comfort_WR / len(conversations),
                    'comfort_LR': comfort_LR / len(conversations),
                }
        print(result)
    elif args.metric == 'autobiography':
        opponent_llm_list = ['gpt-4-turbo', 'gpt-4o', 'llama3-8b', 'llama3-70b', 'mixtral', 'qwen2-72b']
        # opponent_llm_list = ['gpt-4-turbo']
        opponent_autobio_path = './autobiography_generation/baseline-{}/Catherine_Helen_Spence/autobiography.json'
        # opponent_llm_list = ['llama3-8b', 'llama3-70b', 'mixtral', 'qwen2-72b']
        result = {}
        auto_paras = load_autobiography(args.autobio_folder)
        for opponent_llm in tqdm.tqdm(opponent_llm_list):
            opponent_auto_paras = load_autobiography(opponent_autobio_path.format(opponent_llm))

            opponent_auto_paras = opponent_auto_paras * 10
            np.random.shuffle(opponent_auto_paras)
            fluency_WR = 0
            fluency_LR = 0
            question_WR = 0
            question_LR = 0
            comfort_WR = 0
            comfort_LR = 0

            result[opponent_llm] = {}

            for conv, opp_conv in tqdm.tqdm(zip(auto_paras, opponent_auto_paras[:len(auto_paras)])):
                insight_resp = autobio_compare(conv, opp_conv, metric='insightfulness')
                narrative_resp = autobio_compare(conv, opp_conv, metric='narrativity')
                emotion_resp = autobio_compare(conv, opp_conv, metric='emotional')
                # print(insight_resp)
                # print(narrative_resp)
                # print(emotion_resp)
                if '[[A]]' in insight_resp:
                    fluency_WR += 1
                elif '[[B]]' in insight_resp:
                    fluency_LR += 1

                if '[[A]]' in narrative_resp:
                    question_WR += 1
                elif '[[B]]' in narrative_resp:
                    question_LR += 1

                if '[[A]]' in emotion_resp:
                    comfort_WR += 1
                elif '[[B]]' in emotion_resp:
                    comfort_LR += 1

                result[opponent_llm] = {
                    'insightful_WR': fluency_WR / len(auto_paras),
                    'insightful_LR': fluency_LR / len(auto_paras),
                    'narrative_WR': question_WR / len(auto_paras),
                    'narrative_LR': question_LR / len(auto_paras),
                    'emotion_WR': comfort_WR / len(auto_paras),
                    'emotion_LR': comfort_LR / len(auto_paras),
                }
                print(result[opponent_llm])

    else:
        raise NotImplementedError

    result = None
    if result is not None:
        config_name = args.eval_config_path.split('/')[-1]
        model_name = args.conv_history_folder.split('/')[-1]
        if os.path.exists(args.eval_result_path):
            with open(args.eval_result_path, 'r') as f:
                existing_results = json.load(f)
        else:
            existing_results = {}

        # update evaluation results
        if args.metric not in existing_results.keys():
            existing_results[args.metric] = {}

        if config_name not in existing_results[args.metric].keys():
            existing_results[args.metric][config_name] = {}

        if model_name not in existing_results[args.metric][config_name]:
            existing_results[args.metric][config_name][model_name] = {}

        existing_results[args.metric][config_name][model_name] = result
        with open(args.eval_result_path, 'w') as f:
            json.dump(existing_results, f)
