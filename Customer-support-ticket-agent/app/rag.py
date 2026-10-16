import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class RAGService:
    def __init__(self):
        self.vector_store = None
        self.initialize_kb()

    def initialize_kb(self):
        file_path = "data/policies.md"
        if not os.path.exists(file_path):
            return
        
        loader = TextLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        
        # Using lightweight local HuggingFace embeddings to avoid Google API 404 errors
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma.from_documents(splits, embeddings)

    def query(self, question: str):
        if not self.vector_store:
            return "Knowledge base not initialized.", []
        
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})
        docs = retriever.get_relevant_documents(question)
        
        context = "\n".join([doc.page_content for doc in docs])
        sources = list(set([os.path.basename(doc.metadata.get("source", "policies.md")) for doc in docs]))
        
        return context, sources

rag_system = RAGService()