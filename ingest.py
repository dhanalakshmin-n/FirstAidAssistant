import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

DATA_PATH = "data"
PERSIST_DIRECTORY = "vectorstore"

def load_documents():
    documents = []
    
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_PATH, filename))
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["topic"] = filename.replace(".txt", "")
            
            documents.extend(docs)
    
    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=450,
        chunk_overlap=70
    )
    return text_splitter.split_documents(documents)


def create_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    
    vectordb.persist()
    print("Vector store created successfully!")


if __name__ == "__main__":
    docs = load_documents()
    chunks = split_documents(docs)
    create_vectorstore(chunks)
