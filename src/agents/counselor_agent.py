import json
import os

from src.agents.context import Context
from src.utils.utils import load_config
from src.agents.chat_llm import chat_llm
from src.prompts.interview_protocol.procedures import sessions
from src.prompts.counselor_prompts import (construct_system_prompt,
                                           construct_rag_prompt,
                                           construct_emotion_strategy_prompt,
                                           construct_wrapped_instructional_prompts,
                                           construct_summarization_prompt,
                                           construct_less_talkative_strategy_prompt,
                                           construct_conversation_summary_prompt,
                                           construct_therapy_strategy_prompt)


class CounselorAgent:
    def __init__(self, config_path, patient_history_dir) -> None:
        self.agent_config = load_config(config_path)
        # conversation context
        self.context = Context()
        self.session_max_tokens = self.agent_config.session_max_tokens
        self.current_tokens = 0
        # time-indexed memory graph
        self.memory_graph = None
        self.memory_graph_explore = []
        # history_conv
        self._load_history_conversations(patient_history_dir)
        # set default interview protocol index
        self.protocol_index = len(os.listdir(patient_history_dir))
        if len(self.history_conversations) > 0:
            self.hist_conv_summarization = self._summarize_from_conversation(
                source='history_conv')
        else:
            self.hist_conv_summarization = None
        # initialize prompts
        self.system_prompt = None
        self.emotion_prompt = None
        self.therapy_strategy_prompt = None

    def get_current_token(self):
        return self.current_tokens

    def set_memory_graph(self, memory_graph):
        self.memory_graph = memory_graph
        self.memory_graph_explore = self.memory_graph.explore()

    def _load_history_conversations(self, conv_history_dir):
        self.history_conversations = []
        conv_history_name_list = [os.path.join(
            conv_history_dir, _) for _ in sorted(os.listdir(conv_history_dir))]
        for conv_h in conv_history_name_list:
            with open(conv_h) as f:
                raw_file = json.load(f)
                # parse converstion content from raw file
                if 'conversation' in raw_file:
                    for conv in raw_file['conversation']:
                        agent, response = conv[0], conv[1]
                        self.history_conversations.append((agent, response))

    def _rag_from_memory_graph(self, question, source):
        """
        1. decided whether RAG is needed
        2. return retrieved documents if needed; Otherwise return None
        retrieve related documents from source
        :param question: target question
        :param source: where to retrieve, could be the reactivated memory graph or conv history
        :return: retrieved related documents or `None` if RAG is not needed
        """
        if source == 'reactivated_memory':
            pass
        elif source == 'history_conv':
            pass
        else:
            raise NotImplementedError
        return None

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
                # formating tuple, remove redundant Patient:
                conv = f'{item[0]}: {item[1].strip("Patient: ")}'
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

    def _is_patient_less_talkative(self, patient_response, default_word_threshold=10):
        """
        determine if the patient is less talkative by comparing the current response's word count to the average word count of responses 
        from the last available conversation.
        If there is no previous conversation, compare the current response's word count to a predefined threshold.
        Returns:
            bool: True if the patient is less talkative, False otherwise
        """
        if self.history_conversations and self.history_conversations[-1]["conversation"]:
            last_conversation = self.history_conversations[-1]["conversation"]
            patient_responses = [
                response[1] for response in last_conversation if response[0] == "patient"]

            if not patient_responses:
                return len(patient_response.split()) < default_word_threshold

            average_words = sum(len(response.split())
                                for response in patient_responses) / len(patient_responses)
        else:
            return len(patient_response.split()) < default_word_threshold

        return len(patient_response.split()) < average_words

    def _construct_response_prompt(self,
                                   patient_response,
                                   use_emotion_module=False,
                                   therapy_strategy=None,
                                   retrieved=None,
                                   summarization=None,
                                   memory_graph_explore=None):
        # if len(self.context.msg) == 0 and patient_response is None:
        session_prompt = sessions[self.protocol_index]
        system_prompt = construct_system_prompt(summarization, session_prompt=session_prompt)
        print("system_prompt", system_prompt)
        self.context.add_system_prompt(system_prompt)
        # else:
        # NOTE: emotion server is down, change it back after the server is up
        if use_emotion_module and False:
            emotion_prompt = self.emotion_prompt if self.emotion_prompt else construct_emotion_strategy_prompt(
                    patient_response)
        else:
            emotion_prompt = None

        if therapy_strategy:
            therapy_strategy_prompt = self.therapy_strategy_prompt if self.therapy_strategy_prompt else construct_therapy_strategy_prompt(
                    therapy_strategy)
        else:
            therapy_strategy_prompt = None

        if retrieved is not None:
            rag_prompt = construct_rag_prompt(retrieved)
        else:
            rag_prompt = None

        if summarization is not None:
            summarization_prompt = construct_summarization_prompt(
                    summarization)
        else:
            summarization_prompt = None

        less_talkative_strategy_prompt = None
            # if self._is_patient_less_talkative(patient_response):
            #     less_talkative_strategy_prompt = construct_less_talkative_strategy_prompt(
            #         patient_response, last_conversation=self.history_conversations[-1]["conversation"])
            # else:
            #     less_talkative_strategy_prompt = None

        instructional_prompt = construct_wrapped_instructional_prompts(emotion_prompt,
                                                                           therapy_strategy_prompt,
                                                                           rag_prompt,
                                                                           summarization_prompt,
                                                                           less_talkative_strategy_prompt,
                                                                           memory_graph_explore)

        print(instructional_prompt)

        if patient_response is not None:
            self.context.add_user_prompt(
                    patient_response + instructional_prompt)

        return self.context.msg

    def talk_to_patient(self,
                        patient_response=None,
                        use_emotion_module=True,
                        therapy_strategy=True,
                        conversations=None,
                        interview_protocol_index=None):

        retrieved = None
        # update memory graph
        # if patient_response is not None and 'Barack Obama' not in patient_response:
        #     self.memory_graph.add(self.memory_graph.extract_events(patient_response))
        #     print(self.memory_graph)

        # explored_questions = self.memory_graph.explore()
        # if self.memory_graph:
        #     retrieved = self._rag_from_memory_graph()
        # else:
        #     retrieved = None

        if interview_protocol_index is not None:
            self.protocol_index = interview_protocol_index
    
        msgs = self._construct_response_prompt(patient_response=patient_response,
                                               use_emotion_module=use_emotion_module,
                                               therapy_strategy=therapy_strategy,
                                               retrieved=retrieved,
                                               summarization=None,
                                               memory_graph_explore=self.memory_graph_explore)

        response = chat_llm(
            messages=msgs,
            model=self.agent_config.llm_model_path,
            temperature=self.agent_config.temperature,
            max_tokens=self.agent_config.max_tokens,
            n=1,
            timeout=self.agent_config.timeout,
            stop=None,
        )
        self.current_tokens += response["completion_tokens"]
        return response["generations"]
