import json
import os
import tqdm

from src.utils.utils import load_config
from src.agents.chat_llm import chat_llm
from src.memory.prompts import (construct_merge_memory_nodes_prompt,
                                construct_extract_events_from_conversation_prompt,
                                construct_explore_prompt,
                                parse_exploration_questions)


class MemoryNode():

    def __init__(self, event):
        self.event = event
        self.date = event['date']
        self.topic = event['topic']
        self.event_description = event['description']
        self.people_involved = event['people_involved']

    def to_json(self):
        return self.event

    def __str__(self):
        return f'Date: {self.date}\tTopic: {self.topic}\tPeople Involved: {self.people_involved}\tEvent Description: {self.event_description}'


class TimeIndexedMemoryGraph():

    def __init__(self, config_path):
        self.config = load_config(config_path) if config_path is not None else None
        self.time_indexed_memory_chain = []

    def _query(self, prompt):
        msg = [
            {'role': 'user',
             'content': prompt}
        ]
        response = chat_llm(
            messages=msg,
            model=self.config.llm_model_path,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            n=self.config.num_generations,
            timeout=self.config.timeout,
        )
        return response['generations'][0]

    def extract_events(self, conv_history):
        prompt = construct_extract_events_from_conversation_prompt(conv_history)
        generation = self._query(prompt)
        return self._parse_memory_nodes(generation)

    def add(self, memory_nodes: list):
        self.time_indexed_memory_chain += memory_nodes

    def explore(self):

        def _parse_questions(generation):
            question_list = []
            generation_splits = generation.split('\n')
            for n in generation_splits:
                splits = n.strip().split(':')
                if len(splits) == 2:
                    question_list.append(splits[1])
                else:
                    print(f'Item: {n} can\'t extract generated question')
                    continue

            return question_list

        if len(self.time_indexed_memory_chain) > 10:
            node_info = str(self)
            prompt = construct_explore_prompt(node_info)
            generation = self._query(prompt)
            return _parse_questions(generation)
        else:
            return []



    def merge(self, new_memory_nodes):
        current_memory_nodes = self._memory_nodes_to_str(self.time_indexed_memory_chain)
        new_memory_nodes = self._memory_nodes_to_str(new_memory_nodes)
        prompt = construct_merge_memory_nodes_prompt(current_memory_nodes, new_memory_nodes)
        generation = self._query(prompt)
        print('Merged')
        print(generation)
        self.time_indexed_memory_chain = self._parse_memory_nodes(generation)

    @staticmethod
    def _parse_memory_nodes(content):
        parsed_nodes = []
        node_list = content.split('\n')
        for n in node_list:
            splits = n.strip().split('#')
            if len(splits) != 4:
                print(f'Item: {n} can\'t be parsed in a memory node. Skipping ...')
                continue
            else:
                event = {
                    'date': splits[0].split('.')[-1].strip(),
                    'topic': splits[1],
                    'people_involved': splits[2],
                    'description': splits[3]
                }
                parsed_nodes.append(MemoryNode(event))
        return parsed_nodes

    @staticmethod
    def _memory_nodes_to_str(memory_nodes):
        s = ''
        for idx, node in enumerate(memory_nodes):
            s += f'{idx}. {str(node)}\n'
        return s

    def load(self, path):
        with open(path, 'r') as f:
            memory_graph = json.load(f)
        # self.config = memory_graph['config']
        self.time_indexed_memory_chain = [MemoryNode(node) for node in memory_graph['time_indexed_memory_chain']]

    def to_json(self):
        return {
            'config': self.config,
            'time_indexed_memory_chain': [node.to_json() for node in self.time_indexed_memory_chain]
        }

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_json(), f)

    def __str__(self):
        info = ""
        for node in self.time_indexed_memory_chain:
            info += str(node) + '\n'
        return info


def init_from_conversation(conversation):
    prompt = f"""You are given a conversation between a counselor and a social-isolation patient:
    ================== Conversation Begin ==================
    {conversation}
    ================== Conversation End ==================
    Read the conversation carefully and list all the events/moments/stories/experiences alone or with others mentioned by the patient in detail and the date these events happened.
    Please list as many as possible.\n
    Your output should be the following format:
    1. <date>#<topic>#<people-involved>#<description in detail>
    2. <date>#<topic>#<people-involved>#<description in detail>
    e.g.,
    1. 1980 early#Birthday Party#Michelle, Adolf, neighbors#<descriptions of this party in detail> 
    ...
    These events should be ranked in chronological order
    """
    msg = [
        {'role': 'user',
         'content': prompt}
    ]
    # print(prompt)
    response = chat_llm(
        messages=msg,
        model='gpt-4-turbo-preview',
        temperature=0.2,
        max_tokens=4096,
        n=1,
        timeout=600,
        stop=None
    )
    return response['generations'][0]


def merge_memory_nodes(nodes):
    history_list = '\n'.join(nodes)
    prompt = f"""You are given a list of memory nodes:
    ================== Memory Node List 1 Begin ==================
    {history_list}
    ================== Memory Node List 2 End ==================
    Read the two memory node lists carefully and merge the two list. You should recognize redundant items according to their date and event description.
    Please list the merged memory node list.\n
    Your output should be the following format:
    1. date1-event1 description in one sentence 
    2. date2-event2 description in one sentence
    ...
    These events should be ranked in chronological order.
    """
    msg = [
        {'role': 'user',
         'content': prompt}
    ]
    print(prompt)
    response = chat_llm(
        messages=msg,
        model='gpt-4-turbo-preview',
        temperature=0.2,
        max_tokens=4096,
        n=1,
        timeout=600,
        stop=None
    )
    return response['generations'][0]


if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = 'sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE'
    history_memory = []
    for file in tqdm.tqdm(os.listdir(
            '/Users/jinhaoduan/workspace/LLM4SocialIsolation/experiments/conv_history_w_interview_protocol/Obama/')[:]):
        with open(
                f'/Users/jinhaoduan/workspace/LLM4SocialIsolation/experiments/conv_history_w_interview_protocol/Obama/{file}',
                'r') as f:
            conversation = json.load(f)['conversation']
        conv_str = ''
        for c in conversation:
            c[1] = c[1].replace('\n', ' ')
            conv_str += f'{c[0]}: {c[1]}\n'
        print('-' * 20 + file)
        memory_node = init_from_conversation(conv_str)
        history_memory.append(memory_node)
    print(merge_memory_nodes(history_memory))
