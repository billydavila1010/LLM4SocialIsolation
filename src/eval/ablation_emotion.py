
import numpy as np
import os
import json

import tqdm

from src.utils.utils import emotion_detection

def load_doctor_resopnses(conv_folder):
    conv_files = os.listdir(conv_folder)
    conv_files = sorted(conv_files)[:10]
    responses = []
    for conv_f in conv_files:
        with open(os.path.join(conv_folder, conv_f)) as f:
            conv = json.load(f)['conversation']
        for c in conv:
            if c[0] == 'patient':
                role = c[0]
                content = c[1].replace('\n', ' ')
                responses.append(content)
    return responses

def emotion_analysis():
    # path = '../with-empathetic-engagement-detected-emotions.json'
    path = '../with-empathetic-engagement-detected-emotions-patient.json'
    # path = '../no-empathetic-engagement-detected-emotions-patient.json'
    with open(path, 'r') as f:
        emotions = json.load(f)
    emotion_dict = {}
    for pair in emotions:
        sentence = pair[0]
        emotion = pair[1]
        for e in emotion:
            emotion_name = e[0].strip()
            intensity = float(e[1])
            if emotion_name not in emotion_dict.keys():
                emotion_dict[emotion_name] = []
            emotion_dict[emotion_name].append(intensity)
    total_emo_intensity = 0
    for k, v in emotion_dict.items():
        total_emo_intensity += np.sum(v)
        print(k, np.sum(v))

    # for k, v in emotion_dict.items():
    #     print(k, np.sum(v) / total_emo_intensity)


if __name__ == '__main__':
    # path = './experiments/conv_history_w_interview_protocol_w_memorygraph_w_emotion_gpt4o/Obama/conv'
    # path = './experiments/no-emotional-engagement/Obama/conv'
    # responses = load_doctor_resopnses(path)
    # detected_emotions = []
    # for resp in tqdm.tqdm(responses):
    #     emotions = emotion_detection(resp)
    #     detected_emotions.append((resp, emotions))
    #     print(emotions)
    # with open('./no-empathetic-engagement-detected-emotions-patient.json', 'w') as f:
    #     json.dump(detected_emotions, f)
    emotion_analysis()