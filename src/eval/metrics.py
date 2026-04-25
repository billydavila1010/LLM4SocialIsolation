
import json
from src.agents.chat_llm import chat_llm
from src.memory.memory_graph import TimeIndexedMemoryGraph
import argparse
from src.utils.utils import load_config
import os
import json
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import re

from collections import Counter
from multiprocessing import Pool
import gin
import spacy
from .data_stat_utils import Fragments
from .eval_prompts import construct_gpt_eval_prompt, construct_gpt_eval_prompt_simplified

from bert_score_batch import batch_score
from bert_score.utils import lang2model,model2layers,get_tokenizer,get_model


try:
    _en = spacy.load('en_core_web_sm')
except OSError:
    print('Downloading the spacy en_core_web_sm model\n'
        "(don't worry, this will only happen once)", file=stderr)
    from spacy.cli import download
    download('en_core_web_sm')
    _en = spacy.load('en_core_web_sm')

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
    content_after_tag = text[start_idx+len(tag):].strip()
    
    # Split the content by whitespace
    parts = content_after_tag.split()
    
    # If the first part (immediately after the tag) is a number, return it, else return the entire content after the tag
    if tag == "#thescore: ":
        assert parts[0].isdigit()
        return int(parts[0])
    else:
        end_idx = text.find("#", start_idx + 1)
        return content_after_tag if end_idx == -1 else content_after_tag[:end_idx].strip()

def load_chapter_gt_events(conv_fp):
    '''
    match retrieved document to chapters to chapter gt events 
    '''
    with open(conv_fp) as f:
        conv = json.load(f) 

    retrieved = []
    
    for d in conv['patient']['patient_context']:
        content = d['content']
        match = re.search(r'======= Document Begin =========\n(.*?)======= Document End =========', content, re.DOTALL)
        if match:
            if not match.group(1) in retrieved:
                retrieved.append(match.group(1))
    
    with open('assets/autobiography_chapters.json') as f:
        chapters = json.load(f)
    
    retrieved_chapters = []
    for i in retrieved:
        for k, v in chapters.items():
            i_no_space = re.sub(r'\s', '', i)
            v_no_space = re.sub(r'\s', '', v)
            if i_no_space in v_no_space:
                print(f'in {k}')
                if k not in retrieved_chapters:
                    retrieved_chapters.append(k)

    with open("assets/autobiography_pre_event_parsed.json") as f:
        chapters_gt_events = json.load(f)
        
    gt_events = []
    for ch in retrieved_chapters:
        ch_events = []
        for item in chapters_gt_events[ch]:
            time, event = item[0], item[1]
            ch_events.append(f'In {time}, {event}')
        gt_events.append(ch_events)
    
    return gt_events

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
        

def load_events_from_memory_graph(reactivated_events):
    '''
    parse events from memory graph into a lists
    '''
    with open(reactivated_events) as f:
        hypotheses = json.load(f) 
    
    summaries = []
    for item in hypotheses['time_indexed_memory_chain']:
        time, event = item['date'], item['description']
        summaries.append(f'In {time}, {event}')

    return summaries

def get_bert_score(gt_events, gt_embeddings, reactivated_events):
    full_text = load_groundtruth_events(gt_events)
    
    tokenizer = AutoTokenizer.from_pretrained("roberta-large")
    model = AutoModel.from_pretrained("roberta-large")

    if os.path.exists(gt_embeddings):
        gt_embeddings = torch.load(gt_embeddings)
    else:   
        times = []
        gt_events = []
        for ch, items in full_text.items():
            for item in items:
                times.append(item[0])
                gt_events.append(item[1])
        gt_inputs = tokenizer(gt_events, return_tensors="pt", padding=True, truncation=True)
        gt_outputs = model(**gt_inputs)
        gt_embeddings = gt_outputs.last_hidden_state.mean(dim=1).detach().numpy()
    
    if os.path.isdir(reactivated_events):
        max_indices = []
        max_values = []
        for filename in os.listdir(reactivated_events):
            summaries = load_events_from_memory_graph(os.join(reactivated_events,filename))
            max_id, max_v = calculate_each_bert_score(
                model, tokenizer, gt_embeddings, summaries)
            max_indices.append(max_id)
            max_values.append(max_v)
    else:
        summaries = load_events_from_memory_graph(reactivated_events)
        max_indices, max_values = calculate_each_bert_score(
            model, tokenizer, gt_embeddings, summaries)
    return max_indices, max_values
    
    
def calculate_each_bert_score(model, tokenizer, gt_embeddings, summaries):
    memory_inputs = tokenizer(summaries, return_tensors="pt", padding=True, truncation=True)
    memory_outputs = model(**memory_inputs)
    memory_embeddings = memory_outputs.last_hidden_state.mean(dim=1).detach().numpy()

    similarity = np.matmul(memory_embeddings, gt_embeddings.T) / (np.linalg.norm(memory_embeddings) * np.linalg.norm(embeddings))
    max_indices = np.argmax(similarity, axis=1).tolist()
    max_values = np.max(similarity, axis=1).tolist()
    return max_indices, max_values

def calculate_bert_score_v2(gt_events, reactivated_events):
    '''
    calculate bert score with bert_score packages
    '''
    summary2score = {}

    lang='en'
    model_type = lang2model[lang]
    num_layers = model2layers[model_type]
        
    tokenizer = get_tokenizer(model_type=model_type)
    model = get_model(model_type=model_type, num_layers=num_layers, all_layers=False)
    device = "cpu"
    model.to(device)

    for index, summary in enumerate(reactivated_events):
        print(f'process file {index+1}/{len(reactivated_events)}')
        P, R, F1 = batch_score(cands=[summary]*len(gt_events),                   
                            refs=gt_events, 
                            lang='en', verbose=False,
                            tokenizer_input=tokenizer, 
                            model_input=model,
                            device=device,)
        P, R, F1 = P.numpy(), R.numpy(), F1.numpy()
        
        summary2score[index] = {"pred":summary, "P": P, "R": R, "F1": F1}

        summary2score[index]['max_indices'] = {}
        summary2score[index]['max_values'] = {}
        for kk in ['P', 'R', 'F1']:
            max_indice = np.argmax(v[kk]).tolist()
            max_value = np.max(v[kk]).tolist()
            summary2score[index]['max_indices'][kk] = max_indice
            summary2score[index]['max_values'][kk] = max_value

    
    with open('assets/eval_output/memory_graph_bert_score.json', 'w') as f:
        json.dump(summary2score, f)

class Metric:
    def evaluate_example(self, summary, reference):
        raise NotImplementedError

    def evaluate_batch(self, summaries, references, aggregate=True):
        raise NotImplementedError


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

@gin.configurable
class DataStatsMetric(Metric):
    def __init__(self, n_gram=3, n_workers=24, case=False, tokenize=True):
        """
        Data Statistics metric
        Makes use of Newsroom code: \
            https://github.com/lil-lab/newsroom/blob/master/newsroom/analyze/fragments.py
        Calculates extractive statistics such as coverage, density, compression as
            defined in Newsroom paper as well as the percentage of novel n-grams in the
            summary vs the input text and the percentage of n-grams in the summary which are
            repeated

        NOTE: these statistics are meant to be calculated with respect to the source text
            (e.g. news article) as opposed to the reference.

        Args:
                :param n_gram: compute statistics for n-grams up to and including this length
                :param n_workers: number of processes to use if using multiprocessing
                :param case: whether to lowercase input before calculating statistics
                :param tokenize: whether to tokenize the input; otherwise assumes that the input
                    is a string of space-separated tokens
        """
        self.n_gram = n_gram
        self.n_workers = n_workers
        self.case = case
        self.tokenize = tokenize

    def evaluate_example(self, summary, input_text):
        if self.tokenize:
            input_text = _en(input_text, disable=["tagger", "parser", "ner", "textcat"])
            input_text = [tok.text for tok in input_text]
            summary = _en(summary, disable=["tagger", "parser", "ner", "textcat"])
            summary = [tok.text for tok in summary]
        fragments = Fragments(summary, input_text, case=self.case)
        coverage = fragments.coverage()
        density = fragments.density()
        compression = fragments.compression()
        score_dict = {"coverage": coverage, "density": density, "compression": compression}
        tokenized_summary = fragments._norm_summary
        tokenized_text = fragments._norm_text
        score_dict["summary_length"] = len(tokenized_summary)
        for i in range(1, self.n_gram + 1):
            input_ngrams = list(find_ngrams(tokenized_text, i))
            summ_ngrams = list(find_ngrams(tokenized_summary, i))
            input_ngrams_set = set(input_ngrams)
            summ_ngrams_set = set(summ_ngrams)
            intersect = summ_ngrams_set.intersection(input_ngrams_set)
            try:
                score_dict[f"percentage_novel_{i}-gram"] = (len(summ_ngrams_set) \
                    - len(intersect))/float(len(summ_ngrams_set))
                ngramCounter = Counter()
                ngramCounter.update(summ_ngrams)
                repeated = [key for key, val in ngramCounter.items() if val > 1]
                score_dict[f"percentage_repeated_{i}-gram_in_summ"] = len(repeated)/float(len(summ_ngrams_set))
            except ZeroDivisionError:
                continue
        return score_dict

    def evaluate_batch(self, summaries, input_texts, aggregate=True):
        #  aggregate=false get sum of all summaries metrics
        corpus_score_dict = Counter()
        p = Pool(processes=self.n_workers)
        results = p.starmap(self.evaluate_example, zip(summaries, input_texts))
        p.close()
        
        [corpus_score_dict.update(x) for x in results]
        if aggregate:
            for key in corpus_score_dict.keys():
                corpus_score_dict[key] /= float(len(input_texts))
        
        return corpus_score_dict['density'], corpus_score_dict['coverage']

    @property
    def supports_multi_ref(self):
        return False


def calculate_accuracy(gt_events, reactivated_events):
    pass

def calculate_coverage_density(gt_events, reactivated_events):
    full_text = load_groundtruth_events(gt_events)
    
    summaries = load_events_from_memory_graph(reactivated_events)

    metric = DataStatsMetric()
    # copy gt for all event summaries
    density, coverage = metric.evaluate_batch(summaries, [full_text]*len(summaries))
    
    print(f'Coverage: {coverage}, Density: {density}')

    return coverage, density

def get_coverage_density(gt_events, reactivated_events):
    metrics = {}
    if os.path.isdir(reactivated_events):
        for filename in os.listdir(reactivated_events):
            file_path = os.path.join(reactivated_events, filename)
            print(f'Evaluating: {file_path} GT: {gt_events}')
            coverage, density = calculate_coverage_density(gt_events, file_path)
            metrics[filename] = {'coverage': coverage, 
                                 'density': density, 
                                 'reference':gt_events}
    else:
        print(f'Evaluating: {reactivated_events} GT: {gt_events}')
        coverage, density = calculate_coverage_density(gt_events, reactivated_events)
        metrics[reactivated_events] = {'coverage': coverage, 
                                 'density': density, 
                                 'reference':gt_events}
    
    if args.save_to_local:
        output_dir = os.path.join(config.metrics_output_path, os.path.basename(reactivated_events))
        os.makedirs(output_dir, exist_ok=True)
        print(f'save results to {output_dir}.json')
        with open(output_dir+'.json', 'w') as f:
            json.dump(metrics, f)

def gpt_eval(gt_events, reactivated_events):
    config_path = "./src/configs/metric_config.yaml"
    agent_config = load_config(config_path)
    os.environ["OPENAI_API_KEY"] = 'sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE'

    eval_inputs = []
    responses = []

    for extracted in reactivated_events:
        for gt in gt_events:
            # prompt = construct_gpt_eval_prompt(extracted, gt) # 5-point scale
            prompt = construct_gpt_eval_prompt_simplified(extracted, gt) # 2-point scale
            eval_inputs.append(prompt)
    
    for item in eval_inputs:
        msgs = []
        msg = {}
        msg['role'] = "user"
        msg['content'] = item
        msgs.append(msg)
        os.environ["OPENAI_API_KEY"] = 'sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE'

        response = chat_llm(
            messages=msgs,
            model=agent_config.llm_model_path,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            n=1,
            timeout=agent_config.timeout,
            stop=None
        )
        score = extract_content(response['generations'][0])
        responses.append(score)

    assert len(responses) == len(eval_inputs)
    with open('assets/gpt_eval_responses.json', 'w') as f:
        out = zip(eval_inputs, responses)
        json.dump(out, f)
    
    return out
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval-config-path', type=str, default='./src/configs/patient_config.yaml')
    parser.add_argument('--save-to-local', action='store_true')
    args = parser.parse_args()
    config = load_config(args.eval_config_path)

    gt_events = config.autobiography_pre_event_path
    reactivated_events = config.autobiography_pre_memory_path
    gt_embeddings = config.autobiography_pre_event_embeddings \
        if hasattr(config, 'autobiography_pre_event_embeddings') else None
    
    if not (os.path.exists(gt_events) and os.path.isdir(reactivated_events)):
        raise ValueError('Please provide valid paths for ground truth events and reactivated events')
    
    # get_coverage_density(gt_events, reactivated_events)
    get_bert_score(gt_events, gt_embeddings, reactivated_events)

