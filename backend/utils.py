from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.schema.document import Document
from sentence_transformers import SentenceTransformer
import urllib.parse


def get_embedding_function():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


embedding_model = get_embedding_function()


def load_doc(DATA_PATH):
    doc_loader = PyPDFLoader(DATA_PATH)
    return doc_loader.load()


def split_doc(doc: Document):
    chunks = []
    previous_page_content = ""

    for page in doc:
        current_page_content = page.page_content

        if previous_page_content:
            combined_content = (
                previous_page_content.splitlines()[-3:]
                + current_page_content.splitlines()
            )
            combined_content = "\n".join(combined_content)
        else:
            combined_content = current_page_content
        chunks.append(
            Document(
                page_content=combined_content, metadata={"page": page.metadata["page"]}
            )
        )
        previous_page_content = current_page_content
    return chunks


def get_embeddings(model, chunks):
    embeddings = model.encode([chunk.page_content for chunk in chunks])
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


def process_file(file_path):
    doc = load_doc(file_path)
    chunks = split_doc(doc)
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
    return [embeddings, metadata]


def add_data_to_vector_db(vector_store, embeddings, metadata):
    vector_store.add_vectors(embeddings, metadata)


def get_data_and_page_numbers(search_results):
    relevant_data = []
    page_numbers = []
    for data in search_results:
        relevant_data.append(str(data["metadata"]["content"]))
        page_numbers.append(int(data["metadata"]["page"]))
    return relevant_data, page_numbers
