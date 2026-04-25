
import json
import os

import tqdm

from src.memory.memory_graph import TimeIndexedMemoryGraph
from src.utils.utils import load_config


def main():
    with open('../eval_results.json') as f:
        data = json.load(f)

    model_list = ['gpt-4-turbo', 'gpt-4o', 'llama3-70b', 'llama3-8b', 'mixtral', 'qwen2-72b']

    for k, v in data.items():
        print(k)
        for _k, _v in v.items():
            print(_k)
            for m in model_list:
                # for __k, __v in _v.items():
                print(m, _v[m])


def check_num_memory_nodes():
    root = '../experiments/conv_history_w_interview_protocol_w_memorygraph_w_emotion_gpt4o/Obama/memory_graph'
    memfile_lists = sorted([_ for _ in os.listdir(root) if not _.startswith('extracted')])
    num_memory_nodes = []
    num_extrapolated = []
    graph_config = 'src/configs/memory_graph_config.yaml'
    g = TimeIndexedMemoryGraph(load_config(graph_config))
    g.load()
    for mem in memfile_lists:
        with open(os.path.join(root, mem)) as f:
            memory = json.load(f)
            num_memory_nodes.append(len(memory['time_indexed_memory_chain']))
    print(num_memory_nodes)

def check_memory_extrapolation():
    root = '../experiments/conv_history_w_interview_protocol_w_memorygraph_w_emotion_gpt4o/Obama/memory_graph'
    memfile_lists = sorted([_ for _ in os.listdir(root) if not _.startswith('extracted')])
    num_extrapolated = []
    graph_config = '../src/configs/memory_graph_config.yaml'
    for mem in tqdm.tqdm(memfile_lists):
        g = TimeIndexedMemoryGraph(graph_config)
        g.load(os.path.join(root, mem))
        num_extrapolated.append(len(g.explore()))
    print(num_extrapolated)

if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = 'sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE'
    # check_num_memory_nodes()
    check_memory_extrapolation()