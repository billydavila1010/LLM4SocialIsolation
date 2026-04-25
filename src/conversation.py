
import os.path
import copy
from datetime import datetime
import pytz

class Conversation:
    def __init__(self) -> None:
        self.patient_info = ""

        self.conversation = []

        self.patient_out = None
        self.doctor_out = None

        self.patient = None
        self.doctor = None

        self.time_stamp = datetime.now(pytz.timezone('US/Eastern')).strftime("%m/%d/%Y, %H:%M:%S, %f")

    def set_patient(self, patient):
        self.patient = patient
        self.patient_info = {
            "patient_model_config": patient.agent_config,
            # "patient_story": patient.agent_config
        }

    def set_doctor(self, doctor):
        self.doctor = doctor

    def generate_doctor_response(self):
        '''
        Must be called after setting the patient and doctor
        '''
        self.doctor_out = self.doctor.talk_to_patient(self.patient_out, 
                                                      conversations=self.conversation)[0]
        return self.doctor_out

    def generate_patient_response(self):
        '''
        Must be called after setting the patient and doctor
        '''
        self.patient_out = self.patient.talk_to_doctor(self.doctor_out)[0]
        return self.patient_out

    def submit_doctor_response(self, response):
        self.conversation.append(("doctor", response))
        self.doctor.context.add_assistant_prompt(response)

    def submit_patient_response(self, response):
        self.conversation.append(("patient", response))
        self.patient.context.add_assistant_prompt(response)

    def get_virtual_doctor_token(self):
        return self.doctor.current_tokens


    def start_session(self, num_conv_round):
        self.conversation_round = 1
        while True:

            doctor_out = self.generate_doctor_response()
            self.submit_doctor_response(doctor_out)
            print(f'Round {self.conversation_round} Doctor: {doctor_out}')

            patient_out = self.generate_patient_response()
            self.submit_patient_response(patient_out)
            print(f'Round {self.conversation_round} Patient: {patient_out}')

            self.conversation_round += 1
            # Condition when we jump out of the loop
            if self.conversation_round >= num_conv_round:
                break

    def set_condition(self, _type, value=None):
        # TODO not implemented
        pass

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


if __name__ == '__main__':
    os.environ["OPENAI_API_KEY"] = "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"
    c = Conversation()
    c.start_session()
