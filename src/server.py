from src.agents.counselor_agent import CounselorAgent
from src.agents.patient_real_human import PatientRealHuman
from src.utils.utils import save_as_json
from src.memory.memory_graph import TimeIndexedMemoryGraph

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
import argparse
import pytz
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Server:
    def __init__(self) -> None:
        self.patient_info = ""

        self.conversation = []

        self.patient_out = None
        self.doctor_out = None

        self.patient = None
        self.doctor = None

        self.conversation_round = 0
        self.time_stamp = datetime.now(pytz.timezone(

            'US/Eastern')).strftime("%m/%d/%Y, %H:%M:%S, %f")
        self.interview_protocol_index = None

    def set_patient(self, patient):
        self.patient = patient
        self.patient_info = {
            "patient_model_config": patient.agent_config,
        }

    def set_doctor(self, doctor):
        self.doctor = doctor

    def set_interview_protocol_index(self, interview_protocol_index):
        self.interview_protocol_index = interview_protocol_index

    def generate_doctor_response(self):
        '''
        Must be called after setting the patient and doctor
        '''
        self.doctor_out = self.doctor.talk_to_patient(
            self.patient_out, conversations=self.conversation, interview_protocol_index=self.interview_protocol_index)[0]
        return self.doctor_out

    def submit_doctor_response(self, response):
        self.conversation.append(("doctor", response))
        self.doctor.context.add_assistant_prompt(response)

    def submit_patient_response(self, response):
        self.conversation.append(("patient", response))
        self.patient.context.add_assistant_prompt(response)

    def get_response(self, patient_prompt):
        self.patient_out = patient_prompt
        self.submit_patient_response(patient_prompt)
        print(f'Round {self.conversation_round} Patient: {patient_prompt}')
    
        if patient_prompt is not None:
            self.conversation_round += 1

        doctor_out = self.generate_doctor_response()
        self.submit_doctor_response(doctor_out)
        print(f'Round {self.conversation_round} Doctor: {doctor_out}')

        return {"response": doctor_out}

    def to_dict(self):
        return {
            'time_stamp': self.time_stamp,
            'patient': {
                'patient_user_id': self.patient.patient_id,
                'patient_info': self.patient_info,
                'patient_context': self.patient.context.msg
            },
            'doctor': {
                'doctor_model_config': self.doctor.agent_config,
                'doctor_context': self.doctor.context.msg
            },
            "conversation": self.conversation,
        }

    def __json__(self):
        return self.to_dict()


def create_app():
    app = Flask(__name__)
    CORS(app)
    return app


def configure_routes(app, server, conv_history_dir):
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"message": "Welcome to the homepage!"})

    @app.route('/api/set-key', methods=['POST'])
    def set_api_key():
        api_key = request.get_json().get('api_key')
        if not api_key:
            return jsonify({"error": "API key not provided"}), 400
        os.environ["OPENAI_API_KEY"] = api_key
        return jsonify({"message": "API key set successfully"}), 200
    
    @app.route('/api/set-interview-protocol_index', methods=['POST'])
    def set_interview_protocol_index():
        interview_protocol_index = request.get_json().get('interview_protocol_index')
        if not interview_protocol_index:
            return jsonify({"note": "Using default interview protocol"}), 200
        server.set_interview_protocol_index(interview_protocol_index)
        return jsonify({"message": "Interview protocol index set successfully"}), 200
    

    @app.route('/prompts/system', methods=['POST'])
    def set_system_prompt():
        system_prompt = request.get_json().get('system_prompt')
        # NOTE: system_prompt can be None. If None, the default system prompt will be used.
        server.doctor.system_prompt = system_prompt
        return jsonify({"message": "System prompt set successfully"}), 200

    @app.route('/prompts/emotion', methods=['POST'])
    def set_emotion_prompt():
        emotion_prompt = request.get_json().get('emotion_prompt')
        # NOTE: emotion_prompt can be None. If None, the default emotion prompt will be used.
        server.doctor.emotion_prompt = emotion_prompt
        return jsonify({"message": "Emotion prompt set successfully"}), 200

    @app.route('/prompts/therapy-strategy', methods=['POST'])
    def set_therapy_strategy_prompt():
        therapy_strategy_prompt = request.get_json().get('therapy_strategy_prompt')
        # NOTE: therapy_strategy_prompt can be None. If None, the default therapy strategy prompt will be used.
        server.doctor.therapy_strategy_prompt = therapy_strategy_prompt
        return jsonify({"message": "Therapy strategy prompt set successfully"}), 200

    @app.route('/responses/welcome', methods=['POST'])
    def get_welcome_message():
        welcome_message = server.get_response(patient_prompt=None)
        if not welcome_message:
            return jsonify({"error": "Failed to retrieve welcome message"}), 400
        return jsonify({"welcome_message": welcome_message})

    @app.route('/responses/doctor', methods=['POST'])
    def get_response():
        patient_prompt = request.get_json().get('patient_prompt')
        if not patient_prompt:
            return jsonify({"error": "Patient prompt not provided"}), 400
        doctor_response = server.get_response(patient_prompt=patient_prompt)
        return jsonify(doctor_response)

    @app.route('/system/shutdown', methods=['GET'])
    def shutdown():
        """
        Endpoint to gracefully shut down the Flask application.
        """
        timestamp = time.time()
        conv_name = f'{timestamp}.json'
        save_as_json(os.path.join(conv_history_dir,
                     conv_name), server.to_dict())

        # # update memory graph
        # conversation = server.to_dict()['conversation']
        # conv_str = ''
        # for c in conversation:
        #     role = c[0]
        #     content = c[1].replace('\n', ' ')
        #     conv_str += f'{role}: {content}\n'
        # memory_nodes = memory_graph.extract_events(conv_str)
        # print('Extracted Memory Nodes')
        # for n in memory_nodes:
        #     print(n)
        # memory_graph.add(memory_nodes)

        # memory_graph.save(os.path.join(memory_graph_dir, conv_name))
        os.kill(os.getpid(), 9)
        return jsonify({"message": "Server is shutting down..."}), 200


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--patient-config-path', type=str,
                        default='./src/configs/patient_config.yaml')
    parser.add_argument('--counselor-config-path', type=str,
                        default='./src/configs/counselor_config.yaml')
    parser.add_argument('--retriever-config-path', type=str,
                        default='./src/configs/retrievers/faiss_retriever.yaml')
    parser.add_argument('--conversation-history-dir',
                        type=str, default='./experiments/conv_history')
    parser.add_argument('--num-conversation-round', type=int, default=30)
    args = parser.parse_args()

    patient = PatientRealHuman(config_path=args.patient_config_path)

    # conversation history
    patient_id = patient.patient_id
    conv_history_dir = os.path.join(
        args.conversation_history_dir, patient_id, 'conv')
    if not os.path.exists(conv_history_dir):
        os.makedirs(conv_history_dir, exist_ok=True)

    counselor = CounselorAgent(
        config_path=args.counselor_config_path, patient_history_dir=conv_history_dir)

    # # memory graph
    # memory_graph_dir = os.path.join(
    #     args.conversation_history_dir, patient_id, 'memory_graph')
    # if not os.path.exists(memory_graph_dir):
    #     os.makedirs(memory_graph_dir, exist_ok=True)
    # memory_graph = TimeIndexedMemoryGraph(args.memory_graph_config_path)
    # if len(os.listdir(memory_graph_dir)) != 0:
    #     memory_graph.load(os.path.join(memory_graph_dir,
    #                       sorted(os.listdir(memory_graph_dir))[-1]))
    #     print(
    #         f'Loaded MemoryGraph from {memory_graph_dir, sorted(os.listdir(memory_graph_dir))[-1]}')
    # counselor.set_memory_graph(memory_graph)

    server = Server()
    server.set_patient(patient)
    server.set_doctor(counselor)

    app = create_app()
    configure_routes(app, server, conv_history_dir)

    port = int(os.environ.get('PORT', 8080))
    app.run(port=port, host='0.0.0.0', debug=False)


if __name__ == '__main__':
    main()
