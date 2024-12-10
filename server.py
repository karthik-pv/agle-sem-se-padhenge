from flask import Flask, jsonify, request
from utils import (
    load_doc,
    split_doc,
    get_embedding_function,
    get_embeddings,
    search_embeddings,
    get_file_path,
)
from vector_db import FAISSVectorStore


app = Flask(__name__)

vector_store = FAISSVectorStore(dimension=384)


@app.route("/pdf_setup", methods=["POST"])
def pdf_setup():
    data = request.get_json()
    file_url = data["file_url"]
    file_path = get_file_path(file_url)
    doc = load_doc(file_path)
    chunks = split_doc(doc)
    print(chunks)
    return jsonify({"message": "file setup complete"})


if __name__ == "__main__":
    app.run(debug=True)
