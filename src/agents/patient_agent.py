import copy
import uuid

import os
import json

from src.agents.chat_llm import chat_llm
from src.utils.utils import load_config
from src.agents.context import Context

from src.prompts.patient_prompts import (construct_rag_prompt,
                                         construct_conversation_summary_prompt,
                                         construct_autobio_summary_prompt,
                                         construct_incre_autobio_summary_prompt,
                                         construct_wrapped_instructional_prompts,
                                         construct_system_prompt)

from src.retriever.document_retriever.faiss_retriever import FAISSRetriever


class PatientAgent:
    def __init__(self, config_path, doc_retriever_config_path) -> None:
        self.agent_config = load_config(config_path)
        # conversation context
        self.context = Context()
        self.retriever = None
        self.doc_retriever_config_path = doc_retriever_config_path
        self.patient_id = self.agent_config.patient_id
        self.autobiography = self._load_autobiography(self.agent_config.autobiography_path_for_summary)
        if os.path.exists(self.agent_config.autobiography_pre_summary_path):
            with open(self.agent_config.autobiography_pre_summary_path, 'r') as f:
                autobiography_summary = json.load(f)['summary']
        else:
            autobiography_summary = self._summarize_from_autobiography(save_to_local=True)

        self._construct_system_prompt(autobiography_summary)

    @staticmethod
    def _load_autobiography(autobiography_path):
        """
        load autobiography summarization
        :param autobiography_path: path to autobiography
        :return:
        """
        if not os.path.exists(autobiography_path):
            raise FileNotFoundError
        if autobiography_path.endswith('.json'):
            with open(autobiography_path, 'rb') as f:
                autobiography = json.load(f)
        else:
            with open(autobiography_path) as f:
                autobiography = f.read()
        return autobiography

    def _construct_system_prompt(self, patient_personal_experience):
        """
        Construct patient system prompt. Should include at least:
        1. summarization of autobiography
        2. being social isolated
        """
        self.system_prompt = construct_system_prompt(patient_personal_experience)

    def _rag(self, question, source):
        """
        1. decided whether RAG is needed
        2. return retrieved documents if needed; Otherwise return None
        retrieve related documents from source
        :param question: target question
        :param source: where to retrieve, could be the reactivated memory graph or conv history
        :return: retrieved related documents or `None` if RAG is not needed
        """
        if source == 'autobiography':
            if self.retriever == None:
                self.retriever = FAISSRetriever(self.doc_retriever_config_path)
                self.retriever.load(self.agent_config.autobiography_path_for_rag)
            result = self.retriever.retrieve(question)
            if len(result) == 0:
                result = None
            return result
        else:
            raise NotImplementedError

    def _summarize_from_autobiography(self, save_to_local=False):
        msg = {}
        msg['role'] = "user"
        print(f'Start Incremental Summarization from {self.agent_config.autobiography_path_for_summary}')
        previous_chapter_summary = ''
        if isinstance(self.autobiography, dict):
            for chapter, content in self.autobiography.items():
                print(f'Summarize {chapter}, previous chapter summary: \n {previous_chapter_summary}')

                if not previous_chapter_summary:
                    msg['content'] = construct_autobio_summary_prompt(content)
                else:
                    msg['content'] = construct_incre_autobio_summary_prompt(content, previous_chapter_summary)
                chapter_summary_response = chat_llm(
                    messages=[msg],
                    model=self.agent_config.llm_model_path,
                    temperature=self.agent_config.temperature,
                    max_tokens=self.agent_config.max_tokens,  # currently fixed, can be added to config
                    n=1,
                    timeout=self.agent_config.timeout,
                    stop=None
                )
                previous_chapter_summary = chapter_summary_response['generations'][0]
            summary = previous_chapter_summary
            print(f'Finish Incremental Summarization, summary is: \n {summary}')
        else:
            msg['content'] = construct_autobio_summary_prompt(self.autobiography)
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

            if save_to_local:
                with open(self.agent_config.autobiography_pre_summary_path, 'w') as f:
                    json.dump({'summary': summary}, f)

        return summary

    def _summarize_from_conversation(self, conversation):
        msg = {}
        msg['role'] = "user"
        session = []
        for item in conversation:
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

    def _check_need_rag(self, context, doctor_response):
        # check whether RAG is needed
        if len(context.msg) == 0:
            context.add_system_prompt(self.system_prompt)
        prompt = f"""{doctor_response}
        
       ================ Instruction Begin ================
       If the counselor asking some questions regarding your situation that you are not sure about it, you should retrieve the related documents from documents. In this case, you should output the following format:
       <RETRIEVE> <The question you want to retrieve>
       If you think you already have enough knowledge/information to provide response without need to retrieve your external library/journal, you should directly output the following tool-usage signal:
       <NORETRIEVE>
       ================ Instruction End ================
       """
        context.add_user_prompt(prompt)
        response = chat_llm(
            messages=context.msg,
            model=self.agent_config.llm_model_path,
            temperature=self.agent_config.temperature,
            max_tokens=self.agent_config.max_tokens,
            n=1,
            timeout=self.agent_config.timeout,
            stop=None
        )
        response = response['generations'][0]
        if 'NORETRIEVE' in response:
            return None
        elif 'RETRIEVE' in response:
            return response.replace('<', '').replace('>', '').replace('RETRIEVE', '')

    def _construct_response_prompt(self,
                                   doctor_response,
                                   retrieved=None,
                                   summarization=None):

        if len(self.context.msg) == 0:
            self.context.add_system_prompt(self.system_prompt)

        # if retrieved is not None:
        #     rag_prompt = construct_rag_prompt(retrieved)
        # else:
        #     rag_prompt = None
        #
        # if summarization is not None:
        #     summarization_prompt = None
        #     # summarization_prompt = construct_summarization_prompt(summarization)
        # else:
        #     summarization_prompt = None

        instructional_prompt = construct_wrapped_instructional_prompts(retrieved, summarization)

        return doctor_response + '\n' + instructional_prompt

    def talk_to_doctor(self, doctor_response=None):

        assert doctor_response is not None
        # TODO: intergrate conversation summary in conversation
        # summarization = self._summarize(task='conversation', conversation=conversation)
        summarization = None

        prompt = self._construct_response_prompt(doctor_response, retrieved=None, summarization=summarization)
        self.context.add_user_prompt(prompt)

        response = chat_llm(
            messages=self.context.msg,
            model=self.agent_config.llm_model_path,
            temperature=self.agent_config.temperature,
            max_tokens=self.agent_config.max_tokens,
            n=1,
            timeout=self.agent_config.timeout,
            stop=None
        )['generations']

        if 'RETRIEVE' in response[0]:
            print(f'Tool-Usage: {response[0]}')
            self.context.remove_last_prompt()
            retrieve_question = response[0].replace('<', '').replace('>', '').replace('RETRIEVE', '').strip()
            retrieved = self._rag(question=retrieve_question, source='autobiography')

            # TODO: multiple retrieved documents
            if isinstance(retrieved, list):
                retrieved = retrieved[0]
                retrieved = retrieved.page_content.replace('\n', ' ').strip()
            print(f'RETRIEVE document: {retrieved}')

            prompt = self._construct_response_prompt(doctor_response, retrieved=retrieved, summarization=summarization)
            self.context.add_user_prompt(prompt)

            response = chat_llm(
                messages=self.context.msg,
                model=self.agent_config.llm_model_path,
                temperature=self.agent_config.temperature,
                max_tokens=self.agent_config.max_tokens,
                n=1,
                timeout=self.agent_config.timeout,
                stop=None
            )['generations']
            return response
        else:
            return response