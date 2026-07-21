from __future__ import annotations

import os
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"


def load_text_documents() -> list[dict[str, str]]:
    """Load all TXT files from the knowledge base."""
    documents: list[dict[str, str]] = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return documents

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        try:
            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            documents.append(
                {
                    "source": file_path.name,
                    "content": text
                }
            )

        except OSError:
            continue

    return documents


DOCUMENTS = load_text_documents()


def split_into_chunks(
    text: str,
    chunk_size: int = 700
) -> list[str]:
    """Split a document into lightweight text chunks."""
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        combined = f"{current_chunk}\n{paragraph}".strip()

        if len(combined) <= chunk_size:
            current_chunk = combined
        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def tokenize(text: str) -> set[str]:
    """Convert text into searchable keywords."""
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were",
        "what", "which", "how", "can", "could", "do",
        "does", "did", "i", "me", "my", "you", "your",
        "to", "for", "of", "in", "on", "and", "or",
        "with", "about", "please", "tell", "show",
        "give", "need", "want"
    }

    words = re.findall(
        r"[a-z0-9₹]+",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in stop_words and len(word) > 1
    }


def get_products_text() -> str:
    file_path = KNOWLEDGE_BASE_DIR / "products.txt"

    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except OSError:
        return "Product information is currently unavailable."


def get_product_list() -> str:
    return """
Available Products

- TechNova Pro Laptop
- TechNova AirBook
- Nova X10
- Nova X10 Pro
- NovaBuds Wireless Earbuds
- NovaSound Headphones
- NovaWatch Smart
- FastCharge 65W Adapter
- USB-C Cable
- Laptop Backpack
- Wireless Mouse
- Keyboard
""".strip()


def get_specific_product(query_lower: str) -> str | None:
    products_text = get_products_text()

    query_lower = (
        query_lower.lower()
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )

    product_map = {
        "technova pro laptop": [
            "technova pro laptop",
            "pro laptop",
            "technova pro"
        ],
        "technova airbook": [
            "technova airbook",
            "airbook"
        ],
        "nova x10 pro": [
            "nova x10 pro",
            "x10 pro",
            "x10pro"
        ],
        "nova x10": [
            "nova x10",
            "x10"
        ],
        "novabuds wireless earbuds": [
            "novabuds",
            "nova buds",
            "buds",
            "earbuds",
            "earbud",
            "ear pods",
            "earpods",
            "wireless earbuds",
            "wireless earphones",
            "earphones"
        ],
        "novasound headphones": [
            "novasound headphones",
            "novasound",
            "nova sound",
            "headphones",
            "headphone"
        ],
        "novawatch smart": [
            "novawatch smart",
            "novawatch",
            "nova watch",
            "smartwatch",
            "smart watch",
            "watch"
        ],
        "fastcharge 65w adapter": [
            "fastcharge 65w adapter",
            "fastcharge",
            "fast charge",
            "65w adapter",
            "charger",
            "adapter"
        ],
        "usb-c cable": [
            "usb c cable",
            "usb-c cable",
            "type c cable",
            "cable"
        ],
        "laptop backpack": [
            "laptop backpack",
            "laptop bag",
            "backpack",
            "bag"
        ],
        "wireless mouse": [
            "wireless mouse",
            "mouse"
        ],
        "keyboard": [
            "wireless keyboard",
            "keyboard"
        ]
    }

    matched_name = None

    for product_name, aliases in product_map.items():
        if any(alias in query_lower for alias in aliases):
            matched_name = product_name
            break

    if not matched_name:
        return None

    lines = products_text.splitlines()
    product_lines: list[str] = []
    capture = False

    for line in lines:
        clean_line = (
            line.strip()
            .lower()
            .replace("-", " ")
            .replace("_", " ")
        )

        original_clean = line.strip().lower()

        if (
            original_clean.startswith("- ")
            and matched_name in clean_line
        ):
            capture = True
            product_lines.append(line)
            continue

        if capture:
            if original_clean.startswith("- "):
                break

            if line.strip():
                product_lines.append(line)

    if product_lines:
        return "\n".join(product_lines)

    return None


def get_multiple_products(
    query_lower: str
) -> list[str]:

    product_map = {
        "technova pro laptop": [
            "technova pro",
            "pro laptop"
        ],
        "technova airbook": [
            "airbook"
        ],
        "nova x10 pro": [
            "x10 pro",
            "x10pro"
        ],
        "nova x10": [
            "nova x10",
            "x10"
        ],
        "novabuds wireless earbuds": [
            "novabuds",
            "earbuds"
        ],
        "novasound headphones": [
            "novasound",
            "headphones"
        ],
        "novawatch smart": [
            "novawatch",
            "watch"
        ]
    }

    matched_products: list[str] = []

    for product_name, aliases in product_map.items():
        if any(alias in query_lower for alias in aliases):
            matched_products.append(product_name)

    return matched_products


def keyword_search(
    query: str,
    top_k: int = 3
) -> str:
    """Lightweight replacement for vector similarity search."""
    query_tokens = tokenize(query)

    scored_chunks: list[tuple[int, str]] = []

    for document in DOCUMENTS:
        source = document["source"]
        content = document["content"]

        for chunk in split_into_chunks(content):
            chunk_tokens = tokenize(chunk)

            score = len(
                query_tokens.intersection(chunk_tokens)
            )

            lowered_chunk = chunk.lower()

            for token in query_tokens:
                if token in lowered_chunk:
                    score += 1

            scored_chunks.append(
                (
                    score,
                    f"Source: {source}\n{chunk}"
                )
            )

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]

    if not selected:
        return (
            "The requested information was not found in the "
            "TechNova knowledge base."
        )

    return "\n\n".join(selected)


def retrieve_context(
    query: str,
    intent: str | None = None,
    top_k: int = 3
) -> str:
    """
    Retrieve product details or relevant knowledge-base text.

    The optional intent parameter is accepted so this function
    remains compatible with different main.py implementations.
    """

    query_lower = query.lower().strip()

    if query_lower == "all products":
        return get_products_text()

    if "best battery" in query_lower:
        return get_products_text()

    if (
        "under" in query_lower
        and (
            "₹" in query_lower
            or "rs" in query_lower
            or "rupees" in query_lower
        )
    ):
        return get_products_text()

    if "recommend" in query_lower:
        return get_products_text()

    if (
        "compare" in query_lower
        or " vs " in f" {query_lower} "
    ):
        products = get_multiple_products(
            query_lower
        )

        contexts: list[str] = []

        for product in products:
            product_context = get_specific_product(
                product
            )

            if product_context:
                contexts.append(product_context)

        if contexts:
            return "\n\n".join(contexts)

    if any(
        text in query_lower
        for text in [
            "show me your products",
            "show products",
            "available products",
            "list products",
            "list all products",
            "all products",
            "what products",
            "products available",
            "what are your products"
        ]
    ):
        return get_product_list()

    product_context = get_specific_product(
        query_lower
    )

    if product_context:
        return product_context

    return keyword_search(
        query=query,
        top_k=top_k
    )
