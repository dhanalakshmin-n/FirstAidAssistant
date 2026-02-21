from dotenv import load_dotenv
import os

load_dotenv()

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_mistralai.chat_models import ChatMistralAI

PERSIST_DIRECTORY = "vectorstore"


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_qa_chain():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    prompt_template = """
You are an emergency response assistant.

Use ONLY the provided context to answer.

Provide:
- Immediate action
- Step-by-step instructions
- Safety warnings

Context:
{context}

Question:
{question}

Answer:
"""

    PROMPT = PromptTemplate.from_template(prompt_template)

    llm = ChatMistralAI(
        model="mistral-small",
        temperature=0,
        api_key=os.getenv("MISTRAL_API_KEY")
    )

    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return qa_chain


# Create chain once at startup
qa_chain = create_qa_chain()


def ask_question(query: str):
    return qa_chain.invoke(query)