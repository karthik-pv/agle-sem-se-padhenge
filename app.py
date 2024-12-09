from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb

DATA_PATH = "data/CN Module 1 Notes -Data Communications & Networks.pdf"

client = chromadb.Client()
collection = client.create_collection(name="notes")


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


def search_embeddings(query, embeddings_with_metadata, model):
    query_embedding = model.encode([query])

    embeddings = np.array([entry["embedding"] for entry in embeddings_with_metadata])

    similarities = cosine_similarity(query_embedding, embeddings).flatten()

    top_indices = similarities.argsort()[-5:][::-1]

    results = [(embeddings_with_metadata[i], similarities[i]) for i in top_indices]
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

    collection.add(ids=ids, embeddings=embeddings, metadatas=metadata)

    query = "What are the key components in data communications?"
    query_embedding = embedding_model.encode([query])
    print(query_embedding)
    results = collection.query(query_embedding, n_results=5)
    print(results)

except Exception as e:
    print(f"An error occurred: {e}")
