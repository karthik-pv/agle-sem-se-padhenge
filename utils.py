from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from sentence_transformers import SentenceTransformer
import urllib.parse


def load_doc(DATA_PATH):
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


def search_embeddings(query, model, vector_store):
    query_embedding = model.encode([query])
    results = vector_store.search(query_embedding, k=5)
    return results


def get_file_path(file_url):
    if file_url.startswith("file://"):
        file_path = urllib.parse.unquote(file_url[8:])
        return file_path
    else:
        raise ValueError("Invalid file URL")
