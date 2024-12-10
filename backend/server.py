from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import (
    load_doc,
    split_doc,
    get_embedding_function,
    get_embeddings,
    search_embeddings,
    get_file_path,
    process_file,
    add_data_to_vector_db,
    get_data_and_page_numbers,
)
from ai_model import (
    prompt_construct,
    get_response_from_api,
    ai_api_functionality_wrapper,
)
from vector_db import FAISSVectorStore


app = Flask(__name__)
CORS(app)

vector_store = FAISSVectorStore(dimension=384)
embedding_model = get_embedding_function()


@app.route("/pdf_setup", methods=["POST"])
def pdf_setup():
    data = request.get_json()
    file_url = data["file_url"]
    file_path = get_file_path(file_url)
    embeddings_metadata = process_file(file_path)
    add_data_to_vector_db(vector_store, embeddings_metadata[0], embeddings_metadata[1])
    return jsonify({"message": "file setup complete"}), 200


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    query = data["query"]
    results = search_embeddings(query, embedding_model, vector_store)
    relevant_data, page_numbers = get_data_and_page_numbers(results)
    print(relevant_data)
    response = ai_api_functionality_wrapper(query, relevant_data)
    return jsonify({"message": str(response), "page_numbers": page_numbers}), 200


if __name__ == "__main__":
    app.run(debug=True)
