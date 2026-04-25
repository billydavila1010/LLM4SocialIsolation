
import json
import os
import sys
import argparse

import tqdm

from src.agents.chat_llm import chat_llm
from src.prompts.interview_protocol import procedures

def generate_autobiography(chapter_guidance, conversation, memory_nodes):
    prompt = f"""
You are tasked with generating one chapter of a autobiography for a user. You are providing the following components to finish this chapter:
1. A guidance of this chapter
- The chapter should be finished by following this guidance
2. A conversation dialog between the user and the interviewer 
- Tone and Preference: The chapter will simulate the user's tone and preference, leveraging the user's oral habits.
- Content and Details: The chapter will include the contents and details appeared in this conversation.
3. A list of memory nodes that happened during this chapter
- Events: The chapter should include all the events listed in the memory nodes

Now, I will provide you with the three contents.
================ Chapter Guidance Beginning ================
{chapter_guidance}
================ Chapter Guidance Ending ================
================ Conversation Beginning ================
{conversation}
================ Conversation Ending ================
================ Memory Nodes Beginning ================
{memory_nodes}
================ Memory Nodes Ending ================

When generating this chapter, you should make sure it is:
Insightful: Involving a deep, self-reflective exploration of past experiences, with a profound understanding of motives, actions, and impacts. 
Narrative: A compelling, logical, and well-articulated life story, blending memorable anecdotes, vivid descriptions, and insightful reflections
Emotional Impact: Engaging the reader by stirring feelings, evoking empathy, and stirring responses through the author's personal triumphs, challenges, and experiences.

You should summarize all these information and finish this chapter

"""
    return prompt


def generate_autobiography_for_baseline(conversation):
    prompt = f"""
    You are tasked with generating one chapter of a autobiography for a user. You are providing the following components to finish this chapter:
1. A conversation dialog between the user and the interviewer 
- Tone and Preference: The chapter will simulate the interviewer's tone and preference, leveraging the interviewer's oral habits.
- Content and Details: The chapter will include the contents and details appeared in this conversation.

Now, I will provide you with the three contents.
================ Conversation Beginning ================
{conversation}
================ Conversation Ending ================

When generating this chapter, you should make sure it is:
Insightful: Involving a deep, self-reflective exploration of past experiences, with a profound understanding of motives, actions, and impacts. 
Narrative: A compelling, logical, and well-articulated life story, blending memorable anecdotes, vivid descriptions, and insightful reflections
Emotional Impact: Engaging the reader by stirring feelings, evoking empathy, and stirring responses through the author's personal triumphs, challenges, and experiences.

You should summarize all these information and finish this chapter
"""
    return prompt

def load_conversation(path):
    with open(path, 'r') as f:
        conversation = json.load(f)['conversation']
    conv_str = ''
    for c in conversation:
        role = c[0]
        content = c[1].replace('\n', ' ')
        conv_str += f'{role}: {content}\n'
    return conv_str

def load_memory_node(path1, path2=None):
    with open(path1, 'r') as f:
        current = json.load(f)['time_indexed_memory_chain']

    if path2 is not None:
        with open(path2, 'r') as f:
            past = json.load(f)['time_indexed_memory_chain']
        current = current[len(past):]

    # memory node to str
    memory_str = ''
    for idx, node in enumerate(current):
        date = node['date']
        topic = node['topic']
        people_involved = node['people_involved']
        description = node['description']
        memory_str += f'{idx}. Date: {date}\tTopic: {topic}\tPeople Involved: {people_involved}\tDescription: {description}\n'

    return memory_str

if __name__ == '__main__':
    os.environ["OPENAI_API_KEY"] = 'sk-proj-gnsHm641bDW03xVw5NVVT3BlbkFJAdHGoLjtnQudMKofQsAE'
    parser = argparse.ArgumentParser()
    parser.add_argument('--conv-history-folder', type=str, default='./baseline_exp/cat_helen_spence/qwen2-72b')
    parser.add_argument('--memory-graph-folder', type=str, default=None)

    parser.add_argument('--output-folder', type=str, default='./autobiography_generation/')
    args = parser.parse_args()

    llm_name = os.path.basename(args.conv_history_folder)
    conv_root = args.conv_history_folder
    mem_root = args.memory_graph_folder
    autobio = 'Catherine_Helen_Spence'

    autobiography = []
    conv_files = sorted([_ for _ in os.listdir(args.conv_history_folder) if not _.startswith('extracted')])
    for i in tqdm.tqdm(range(len(conv_files))):
        # load guidance
        guidance = procedures.sessions[i]['prompt']
        # load conversation
        conv_name = conv_files[i]
        conversation = load_conversation(os.path.join(conv_root, conv_name))
        if mem_root is not None:
            save_path = os.path.join(args.output_folder, 'guidellm', autobio)
            # for GuideLLM
            # load memory nodes
            current_mem_name = sorted(os.listdir(mem_root))[i]
            if i != 0:
                past = os.path.join(mem_root, sorted(os.listdir(mem_root))[i - 1])
            else:
                past = None
            memory_str = load_memory_node(path1=os.path.join(mem_root, current_mem_name), path2=past)
            prompt = generate_autobiography(guidance, conversation, memory_str)
        else:
            save_path = os.path.join(args.output_folder, f'baseline-{llm_name}', autobio)
            # for baseline agents
            prompt = generate_autobiography_for_baseline(conversation)

        msg = [
            {'role': 'user',
             'content': prompt}
        ]
        response = chat_llm(
            messages=msg,
            model='gpt-4o',
            temperature=0.2,
            max_tokens=4096,
            n=1,
            timeout=600,
            stop=None
        )
        gen = response['generations'][0]
        autobiography.append(gen)
        print(gen)

    os.makedirs(save_path, exist_ok=True)
    with open(os.path.join(save_path, 'autobiography.json'), 'w') as f:
        json.dump(autobiography, f)
