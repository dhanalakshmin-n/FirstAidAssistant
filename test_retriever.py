from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

PERSIST_DIRECTORY = "vectorstore"

def test_query(query):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )

    results = vectordb.similarity_search(query, k=3)

    print("\n🔎 Query:", query)
    print("\n📄 Top Results:\n")

    for i, doc in enumerate(results, 1):
        print(f"Result {i}:")
        print(doc.page_content)
        print("-" * 50)


if __name__ == "__main__":
    test_query("How to treat severe bleeding?")
