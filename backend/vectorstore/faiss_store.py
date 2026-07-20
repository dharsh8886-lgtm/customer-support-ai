import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

index = None
documents = []


def create_vector_store(text_chunks):
    global index, documents

    documents = text_chunks

    embeddings = model.encode(
        text_chunks,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(
        np.asarray(
            embeddings,
            dtype="float32"
        )
    )

    return index


def search_vector_store(query, top_k=3):
    if index is None:
        return []

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        np.asarray(
            query_embedding, dtype="float32"
        ),
        top_k
    )

    results = []

    for item_index in indices[0]:
        if 0 <= item_index < len(documents):
            results.append(documents[item_index])

    return results
