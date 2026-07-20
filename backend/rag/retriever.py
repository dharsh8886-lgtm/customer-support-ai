import os

from vectorstore.faiss_store import (
    create_vector_store,
    search_vector_store
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

KNOWLEDGE_BASE_DIR = os.path.join(
    BASE_DIR,
    "knowledge_base"
)


def load_knowledge_base():
    chunks = []

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):

        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(
            KNOWLEDGE_BASE_DIR,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            text = file.read()

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n")
            if paragraph.strip()
        ]

        for paragraph in paragraphs:
            chunks.append(
                f"Source: {filename}\n{paragraph}"
            )

    if chunks:
        create_vector_store(chunks)

    return chunks


def retrieve_context(query, top_k=3):
    return search_vector_store(
        query,
        top_k=top_k
    )
