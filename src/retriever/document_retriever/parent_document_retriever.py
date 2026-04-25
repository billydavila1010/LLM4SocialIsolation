from src.retriever.document_retriever.base_document_retriever import BaseDocumentRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ParentDocRetriever(BaseDocumentRetriever):
    def __init__(self) -> None:
        super().__init__()
    
    def load(self, document_path):
        super().load(document_path)
        parent_splitter = CharacterTextSplitter(separator='.\n')
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
        vectorstore = Chroma(
            collection_name="split_parents", embedding_function=OpenAIEmbeddings()
        )
        store = InMemoryStore()
        self.retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )
        print("adding docs...")
        self.retriever.add_documents(self.data, ids=None)
        print("success")
        
        return 
    
    def retrieve(self,query):
        res=self.retriever.get_relevant_documents(query)
        return res
    