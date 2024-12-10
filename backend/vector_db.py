import faiss
import numpy as np


class FAISSVectorStore:
    def __init__(self, dimension):
        self.index = faiss.IndexFlatIP(dimension)
        self.vectors = []
        self.metadata = []

    def add_vectors(self, vectors, metadata=None):
        vectors_array = np.array(vectors).astype("float32")
        faiss.normalize_L2(vectors_array)
        self.index.add(vectors_array)
        self.vectors.extend(vectors)
        self.metadata.extend(metadata or [{}] * len(vectors))

    def search(self, query_vector, k=5):
        query_vector = np.array(query_vector).astype("float32")
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector.reshape(1, -1), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            results.append(
                {
                    "metadata": self.metadata[idx],
                    "distance": dist,
                    "embedding": self.vectors[idx],
                }
            )

        return results
