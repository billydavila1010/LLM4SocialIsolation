from src.agents.patient_agent import PatientAgent
from src.utils.utils import load_config
from src.agents.context import Context

class PatientRealHuman(PatientAgent):
    def __init__(self, config_path) -> None:
        self.agent_config = load_config(config_path)
        # conversation context
        self.context = Context()
        self.patient_id = self.agent_config.patient_id
        
    def talk_to_doctor(self, doctor_response=None):
        
        return 
