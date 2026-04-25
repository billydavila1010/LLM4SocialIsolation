from src.retriever.document_retriever.base_document_retriever import BaseDocumentRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from src.utils.utils import load_config

class FAISSRetriever(BaseDocumentRetriever):
    def __init__(self, config_path) -> None:
        super().__init__(config_path)
        config=load_config(config_path)
        self.search_type=config.search_type
        self.search_kwargs=config.search_kwargs
        
    def load(self, document_path):
        super().load(document_path)
        text_splitter = CharacterTextSplitter(separator='.\n')
        texts = text_splitter.split_documents(self.data)
        embeddings = OpenAIEmbeddings()
        self.retriever = FAISS.from_documents(texts, embeddings).\
        as_retriever(search_type=self.search_type, search_kwargs=self.search_kwargs)
    
    def retrieve(self,query):
        docs = self.retriever.get_relevant_documents(query)
        print(f"Retrieved {len(docs)} items")
        return docs