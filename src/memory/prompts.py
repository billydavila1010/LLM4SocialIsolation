def construct_extract_events_from_conversation_prompt(conversation):
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
    return prompt

def construct_explore_prompt(memory_node_info):
    prompt = f"""You are given a list of memory nodes from a user's life, which include events and details about those events.
Your task is to reactivate the user's memory by generating some questions to ask the user, Your generated questions should potentially fulfill the memory nodes. 
Each memory node contains a Date, Topic, Involved People, and a Description of the event. Here are the memory nodes:
================== Memory Node Begin ==================
{memory_node_info}
================== Memory Node End ==================
Here are some examples of how you can frame your questions:
If you notice there are no events recorded during a certain period, like youth or old age, you could ask: "I see there's not much about your youth/old age. What happened during that time?"
If a certain person appears multiple times, you might ask: "I noticed that <name> comes up often. Why is <name> important to you?"
If someone appears in a significant event, you could ask: "<name> seems to play a key role in this event. Is there more to the story with <name>?"
Similarly, you should discovery other situations and frame questions from the existing memory nodes. Remember you task is to make the user talk more about their memory and fulfill the memory nodes. Thus, you should explore all the possible and reasonable questions.
Your output should be the following format:
1. Question: <generated question>
2. Question: <generated question>
...
e.g.,
1. Question: I notice you didn't talk much about your youth, what happened during this period?
    """
    return prompt

def construct_merge_memory_nodes_prompt(memory_list1, memory_list2):
    prompt = f"""You are given two lists of memory nodes: existing memory nodes and new memory nodes. 
You are tasked to insert new memory nodes to the existing node list.
================== Existing Memory Node Begin ==================
{memory_list1}
================== Existing Memory Node End ==================
================== New Memory Node Begin ==================
{memory_list2}
================== New Memory Node End ==================
Read the two memory node lists carefully.
Please list the merged memory node list.\n
Your output should be the following format:
1. <event-date>#<topic>#<people-involved>#<description in detail>
2. <event-date>#<topic>#<people-involved>#<description in detail>
e.g.,
1. 1980 early#Birthday Party#Michelle, Adolf, neighbors#<descriptions of this party in detail> 
...

These events should be ranked in chronological order.
"""
    return prompt



def parse_exploration_questions(content):
    pass
