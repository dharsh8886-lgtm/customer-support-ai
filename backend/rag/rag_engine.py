import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")


def load_documents():
    documents = []
    for file_name in os.listdir(KNOWLEDGE_BASE_DIR):
        if file_name.endswith(".txt"):
            file_path = os.path.join(KNOWLEDGE_BASE_DIR, file_name)
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())
    return documents


def create_vector_store():
    documents = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.from_documents(chunks, embeddings)


vector_store = create_vector_store()


def get_products_text():
    file_path = os.path.join(KNOWLEDGE_BASE_DIR, "products.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_product_list():
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
"""


def get_specific_product(query_lower):
    products_text = get_products_text()

    # Normalize the user query
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

        # Keep X10 Pro before X10
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

    # Find matching product from aliases
    for product_name, aliases in product_map.items():
        if any(alias in query_lower for alias in aliases):
            matched_name = product_name
            break

    if not matched_name:
        return None

    # Extract only the matching product block from products.txt
    lines = products_text.splitlines()
    product_lines = []
    capture = False

    for line in lines:
        clean_line = (
            line.strip()
            .lower()
            .replace("-", " ")
            .replace("_", " ")
        )

        original_clean = line.strip().lower()

        # Detect the required product heading
        if original_clean.startswith("- ") and matched_name in clean_line:
            capture = True
            product_lines.append(line)
            continue

        if capture:
            # Stop when the next product begins
            if original_clean.startswith("- "):
                break

            if line.strip():
                product_lines.append(line)

    if product_lines:
        return "\n".join(product_lines)

    return None

def get_multiple_products(query_lower):

    product_map = {
        "technova pro laptop": ["technova pro", "pro laptop"],
        "technova airbook": ["airbook"],
        "nova x10 pro": ["x10 pro"],
        "nova x10": ["nova x10", "x10"],
        "novabuds wireless earbuds": ["novabuds", "earbuds"],
        "novasound headphones": ["novasound", "headphones"],
        "novawatch smart": ["novawatch", "watch"]
    }

    matched_products = []

    for product_name, aliases in product_map.items():

        if any(alias in query_lower for alias in aliases):
            matched_products.append(product_name)

    return matched_products

def retrieve_context(query):
    query_lower = query.lower().strip()

    if query_lower == "all products":

         return get_products_text()

    if "best battery" in query_lower:
         return get_products_text()

    if "under" in query_lower and "₹" in query_lower:
         return get_products_text()

    if "recommend" in query_lower:
         return get_products_text()
    
    if "compare" in query_lower or "vs" in query_lower:

        products = get_multiple_products(query_lower)

        contexts = []

        for product in products:

            product_context = get_specific_product(product)

            if product_context:
                contexts.append(product_context)

        return "\n\n".join(contexts)

    # Show only product names
    if any(text in query_lower for text in [
        "show me your products",
        "show products",
        "available products",
        "list products",
        "list all products",
        "all products",
        "what products",
        "products available",
        "what are your products"
    ]):
        return get_product_list()

    # Show one matching product
    product_context = get_specific_product(query_lower)

    if product_context:
        return product_context

    # Other knowledge-base queries
    results = vector_store.similarity_search(query, k=1)

    return "\n\n".join(
        doc.page_content for doc in results
    )
