# test_calculator.py
import unittest
from src.agents.patient_agent import PatientAgent
from src.retriever.document_retriever.faiss_retriever import FAISSRetriever
import os
class PatientAgentRAG(unittest.TestCase):
    
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = ""
        self.ret=FAISSRetriever('src/configs/retrievers/faiss_retriever.yaml')
        self.ret.load('assets/autobiography/13991012000013_Test.txt')
        
    def test_rag_should_retrieve(self):
        results=self.ret.search("When did the author write this book?")
        if results!=[]:
            self.assertTrue(len(results)>0)
    
    def test_rag_should_not_retrieve(self):
        results=self.ret.search("What is Large Language Model")
        self.assertTrue(results==[])


if __name__ == '__main__':
    unittest.main()
