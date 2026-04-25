
import json

with open('/Users/jinhaoduan/workspace/LLM4SocialIsolation/experiments/conv_history_w_interview_protocol/Obama/1714479442.251891.json') as f:
    conv = json.load(f)['conversation']

for idx, c in enumerate(conv):
    c[1] = c[1].replace('\n', ' ')
    print(f'Round {idx//2} {c[0]} {c[1]}')