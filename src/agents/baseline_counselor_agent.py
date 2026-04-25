import json
import os

from src.agents.context import Context
from src.utils.utils import load_config
from src.agents.chat_llm import chat_llm
from src.prompts.baseline_counselor_prompt import (construct_system_prompt,
                                                   construct_session_topic_prompt,
                                                    construct_conversation_summary_prompt)

class BaselineCounselorAgent:
    def __init__(self, config_path, patient_history_dir) -> None:
        self.agent_config = load_config(config_path)
        # conversation context
        self.context = Context()
        # history_conv
        self._load_history_conversations(patient_history_dir)
        # summarization = None
        if len(self.history_conversations) > 0:
            self.hist_conv_summarization = self._summarize_from_conversation(source='history_conv')
        else:
            self.hist_conv_summarization = None

    def _load_history_conversations(self, conv_history_dir):
        self.history_conversations = []
        conv_history_name_list = [os.path.join(conv_history_dir, _) for _ in sorted(os.listdir(conv_history_dir))]
        for conv_h in conv_history_name_list:
            with open(conv_h) as f:
                raw_file = json.load(f)
                # parse converstion content from raw file
                if 'conversation' in raw_file:
                    for conv in raw_file['conversation']:
                        agent, response = conv[0], conv[1]
                        self.history_conversations.append((agent, response))
    
    def _summarize_from_conversation(self, source):
        """
        1. decided whether summarization is needed
        2. return summarization if needed; Otherwise return None
        :param question: target question/content (if needed)
        :param source: options: reactivated_memory, history_conv
        :return: summarized content or `None` if summarize is not needed
        """
        if source == 'reactivated_memory':
            pass
        elif source == 'history_conv':
            msg = {}
            msg['role'] = "user"
            session = []
            for item in self.history_conversations:
                conv = f'{item[0]}: {item[1].strip("Patient: ")}'  # formating tuple, remove redundant Patient:
                session.append(conv)
            sessions = '\n'.join(session)

            msg['content'] = construct_conversation_summary_prompt(sessions)
            summary_response = chat_llm(
                messages=[msg],
                model=self.agent_config.llm_model_path,
                temperature=self.agent_config.temperature,
                max_tokens=self.agent_config.max_tokens,
                n=1,
                timeout=self.agent_config.timeout,
                stop=None
            )

            summary = summary_response['generations'][0]
            return summary
        else:
            raise NotImplementedError
        return None

    def _construct_response_prompt(self,patient_response, summarization=None):
        if len(self.context.msg) == 0 and patient_response is None:
            # a new conversation
            system_prompt = construct_system_prompt(summarization)
            # get session topic
            session_topic_prompt = construct_session_topic_prompt()
            msg = {}
            msg['role'] = "user"
            msg['content'] = system_prompt + session_topic_prompt

            session_topic_response = chat_llm(
                        messages=[msg],
                        model=self.agent_config.llm_model_path,
                        temperature=self.agent_config.temperature,
                        max_tokens=self.agent_config.max_tokens,
                        n=1,
                        timeout=self.agent_config.timeout,
                        stop=None
                    )

            session_topic = session_topic_response['generations'][0]
            print("session_topic: ", session_topic)
            system_prompt += f"In this talk, you should discuss the topic: {session_topic}\n."
            self.context.add_system_prompt(system_prompt)
        else:
            self.context.add_user_prompt(patient_response)
        return self.context.msg
    
    def talk_to_patient(self,
                        patient_response=None,
                        use_emotion_module=False,
                        therapy_strategy=None,
                        conversations=None):
        msgs = self._construct_response_prompt(patient_response=patient_response, 
                                               summarization=self.hist_conv_summarization)
        response = chat_llm(
            messages=msgs,
            model=self.agent_config.llm_model_path,
            temperature=self.agent_config.temperature,
            max_tokens=self.agent_config.max_tokens,
            n=1,
            timeout=self.agent_config.timeout,
            stop=None,
        )
        return response["generations"]
