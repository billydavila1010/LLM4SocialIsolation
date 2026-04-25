
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


class BaseDocumentRetriever:
    '''
    Do not create a instance of this class, this is an abastract class
    '''
    def __init__(self,config_path) -> None:
        
        pass
    def load(self,document_path):
        '''
        load document from given path

        Args:
            doc_path (str): Path of the document to be retrieved
            
        Returns:
        None: Nothing
        '''
        if document_path.endswith(".txt"):
            loader = TextLoader(document_path)
            self.data=loader.load()
        else:
            raise ValueError("Error: File format is incompatible.")
        
        pass
    
    def retrieve(self,query):
        '''
        retrieve related info according to the query

        Args:
            query (str): The question 
            
        Returns:
        list: list of strings of documents
        '''
        pass

