from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = "data/CN Module 1 Notes -Data Communications & Networks.pdf"


def load_doc():
    doc_loader = PyPDFLoader(DATA_PATH)
    return doc_loader.load()


def split_doc(doc: Document):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=80, length_function=len, is_separator_regex=False
    )
    return text_splitter.split_documents(doc)


def get_embedding_function():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def get_embeddings(model, chunks):
    embeddings = model.encode([chunk.page_content for chunk in chunks])
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
    embeddings = get_embeddings(get_embedding_function(), chunks)
    embeddings_with_page_numbers = []
    for i, chunk in enumerate(chunks):
        page_number = chunk.metadata.get("page", "Unknown")
        embeddings_with_page_numbers.append(
            {"embedding": embeddings[i], "page": page_number}
        )
    query = "What are the key components in data communications?"
    results = search_embeddings(
        query, embeddings_with_page_numbers, get_embedding_function()
    )
    print(results)
    for entry, similarity in results:
        print(f"Page Number: {entry['page']}, Similarity: {similarity:.4f}")

except Exception as e:
    print(f"An error occurred: {e}")
