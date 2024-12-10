from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from sentence_transformers import SentenceTransformer
from vector_db import FAISSVectorStore


DATA_PATH = "data/CN Module 1 Notes -Data Communications & Networks.pdf"


vector_store = FAISSVectorStore(dimension=384)


def load_doc():
    doc_loader = PyPDFLoader(DATA_PATH)
    return doc_loader.load()


def split_doc(doc: Document):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(doc)


def get_embedding_function():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def get_embeddings(model, chunks):
    embeddings = model.encode([chunk.page_content for chunk in chunks])
    print(embeddings)
    return embeddings


def search_embeddings(query, model):
    query_embedding = model.encode([query])
    results = vector_store.search(query_embedding, k=5)
    return results


try:
    doc = load_doc()
    chunks = split_doc(doc)

    embedding_model = get_embedding_function()
    embeddings = get_embeddings(embedding_model, chunks)

    ids = []
    metadata = []
    for i, chunk in enumerate(chunks):
        ids.append(str(i))
        metadata.append(
            {
                "id": i,
                "page": chunk.metadata["page"],
                "content": chunk.page_content,
            }
        )

    vector_store.add_vectors(embeddings, metadata)

    query = "What are the key components in data communications?"
    query_embedding = embedding_model.encode([query])
    print(query_embedding)

    results = search_embeddings(query, vector_store.vectors, embedding_model)

    for result in results:
        print("\nResult:")
        print("Similarity Score:", result["distance"])
        print("Page:", result["metadata"].get("page", "N/A"))
        print("Content Snippet:", result["metadata"].get("content", "N/A"))

except Exception as e:
    print(f"An error occurred: {e}")
