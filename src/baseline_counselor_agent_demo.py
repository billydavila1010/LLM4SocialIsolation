import os.path
import argparse
import time

from src.conversation import Conversation
from src.agents.baseline_counselor_agent import BaselineCounselorAgent
from src.agents.patient_agent import PatientAgent
from src.utils.utils import save_as_json

def main(args):

    patient = PatientAgent(config_path=args.patient_config_path, doc_retriever_config_path=args.retriever_config_path)

    # conversation history
    patient_id = patient.patient_id
    conv_history_dir = os.path.join(args.conversation_history_dir, patient_id, 'conv')
    if not os.path.exists(conv_history_dir):
        os.makedirs(conv_history_dir, exist_ok=True)

    counselor = BaselineCounselorAgent(config_path=args.counselor_config_path, patient_history_dir=conv_history_dir)

    conversation = Conversation()
    conversation.set_patient(patient)
    conversation.set_doctor(counselor)
    conversation.start_session(num_conv_round=args.num_conversation_round)

    timestamp = time.time()
    conv_name = f'{timestamp}.json'
    save_as_json(os.path.join(conv_history_dir, conv_name), conversation.to_dict())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--patient-config-path', type=str, default='./src/configs/patient_config.yaml')
    parser.add_argument('--counselor-config-path', type=str, default='./src/configs/counselor_config.yaml')
    parser.add_argument('--retriever-config-path', type=str, default='./src/configs/retrievers/faiss_retriever.yaml')
    parser.add_argument('--memory-graph-config-path', type=str, default='./src/configs/memory_graph_config.yaml')
    parser.add_argument('--conversation-history-dir', type=str, default='./experiments/conv_history_w_interview_protocol_w_memorygraph')
    parser.add_argument('--num-conversation-round', type=int, default=30)
    parser.add_argument('--openai-api-key', type=str, default=None)
    args = parser.parse_args()

    os.environ["OPENAI_API_KEY"] = args.openai_api_key

    main(args)
