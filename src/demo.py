import os.path
import argparse
import time

from src.conversation import Conversation
from src.agents.counselor_agent import CounselorAgent
from src.agents.patient_agent import PatientAgent
from src.utils.utils import save_as_json
from src.memory.memory_graph import TimeIndexedMemoryGraph

def main(args):

    patient = PatientAgent(config_path=args.patient_config_path, doc_retriever_config_path=args.retriever_config_path)

    # conversation history
    patient_id = patient.patient_id
    conv_history_dir = os.path.join(args.conversation_history_dir, patient_id, 'conv')
    if not os.path.exists(conv_history_dir):
        os.makedirs(conv_history_dir, exist_ok=True)

    counselor = CounselorAgent(config_path=args.counselor_config_path, patient_history_dir=conv_history_dir)

    # memory graph
    memory_graph_dir = os.path.join(args.conversation_history_dir, patient_id, 'memory_graph')
    if not os.path.exists(memory_graph_dir):
        os.makedirs(memory_graph_dir, exist_ok=True)
    memory_graph = TimeIndexedMemoryGraph(args.memory_graph_config_path)
    if len(os.listdir(memory_graph_dir)) != 0:
        memory_graph.load(os.path.join(memory_graph_dir, sorted(os.listdir(memory_graph_dir))[-1]))
        print(f'Loaded MemoryGraph from {memory_graph_dir, sorted(os.listdir(memory_graph_dir))[-1]}')
    counselor.set_memory_graph(memory_graph)

    conversation = Conversation()
    conversation.set_patient(patient)
    conversation.set_doctor(counselor)
    conversation.start_session(num_conv_round=args.num_conversation_round)

    timestamp = time.time()
    conv_name = f'{timestamp}.json'
    save_as_json(os.path.join(conv_history_dir, conv_name), conversation.to_dict())

    # update memory graph
    conversation = conversation.to_dict()['conversation']
    conv_str = ''
    for c in conversation:
        role = c[0]
        content = c[1].replace('\n', ' ')
        conv_str += f'{role}: {content}\n'
    memory_nodes = memory_graph.extract_events(conv_str)
    print('Extracted Memory Nodes')
    for n in memory_nodes:
        print(n)
    memory_graph.add(memory_nodes)

    memory_graph.save(os.path.join(memory_graph_dir, conv_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--patient-config-path', type=str, default='./src/configs/jane_eyre_config.yaml')
    parser.add_argument('--counselor-config-path', type=str, default='./src/configs/counselor_config.yaml')
    parser.add_argument('--retriever-config-path', type=str, default='./src/configs/retrievers/faiss_retriever.yaml')
    parser.add_argument('--memory-graph-config-path', type=str, default='./src/configs/memory_graph_config.yaml')
    # parser.add_argument('--conversation-history-dir', type=str, default='./experiments/conv_history_w_interview_protocol_w_memorygraph')
    parser.add_argument('--conversation-history-dir', type=str, default='./experiments/jane_eyre')
    parser.add_argument('--num-conversation-round', type=int, default=10)
    parser.add_argument('--openai-api-key', type=str, default=None)
    args = parser.parse_args()

    os.environ["OPENAI_API_KEY"] = args.openai_api_key

    main(args)
